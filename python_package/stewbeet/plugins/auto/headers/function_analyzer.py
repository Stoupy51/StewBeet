"""
Function relationship analysis for Minecraft datapack headers.

This module handles building the relationships between functions, tags,
advancements, and function calls to create the @within information.
"""

# pyright: reportUnnecessaryIsInstance=false
# Imports
import re
from typing import cast

from beet import Context

from .execution_parser import parse_execution_context_from_line
from .object import Header

FUNCTION_CALL_RE = re.compile(r"function\s+([#]?[\w./-]+:[\w./-]+)")

# A *command* call to a function: the "function" keyword sits at the start of the command (after an
# optional "$" macro prefix), or right after "run "/"schedule ". This deliberately excludes
# references that live inside an argument
# string — most commonly a tellraw suggest_command/run_command like "/function ns:foo" — whose
# trailing JSON must never be mistaken for a macro ({...}) or a schedule time (100t). Note "run "
# also appears inside quoted dialog commands (`command:"/execute ... run function ns:foo"`), so a
# regex match is only a real command when it is NOT inside a string — see is_inside_string.
COMMAND_CALL_RE = re.compile(r"(?:^\s*\$?\s*|\brun\s+|(?P<sched>\bschedule\s+))function\s+([#]?[\w./-]+:[\w./-]+)")


# Class
class FunctionAnalyzer:
    """ Analyzes function relationships and builds @within information. """

    def __init__(self, ctx: Context, mcfunctions: dict[str, Header]):
        """ Initialize the function analyzer.

        Args:
            ctx (Context): The beet context
            mcfunctions (Dict[str, Header]): Dictionary mapping function paths to Header objects
        """
        self.ctx = ctx
        self.mcfunctions = mcfunctions

    def analyze_function_tags(self) -> None:
        """ Analyze function tags and build relationships. """
        # For each function tag, get the functions that it calls
        for tag_path, tag in self.ctx.data.function_tags.items():
            # Get string that is used for calling the function (ex: "#namespace:my_function")
            to_be_called: str = f"#{tag_path}"

            # Loop through the functions in the tag
            for function_path in tag.data["values"]:
                if isinstance(function_path, str):
                    if function_path in self.mcfunctions:
                        self.mcfunctions[function_path].within.append(to_be_called)
                elif isinstance(function_path, dict):
                    function_path_str: str = cast(dict[str,str],function_path).get("id", "")
                    if function_path_str in self.mcfunctions:
                        self.mcfunctions[function_path_str].within.append(to_be_called)

    def analyze_advancements(self) -> None:
        """ Analyze advancements and build relationships. """
        # For each advancement, get the functions that it calls
        for adv_path, adv in self.ctx.data.advancements.items():
            # Get string that is used for calling the function (ex: "advancement namespace:my_function")
            to_be_called: str = f"advancement {adv_path}"

            # Check if the advancement has a function reward
            if adv.data.get("rewards", {}).get("function"):
                function_path: str = adv.data["rewards"]["function"]
                if function_path in self.mcfunctions:
                    self.mcfunctions[function_path].within.append(to_be_called)

    def analyze_dialogs(self) -> None:
        """ Analyze dialogs and build relationships.

        A dialog's ``run_command`` / ``suggest_command`` actions carry their command as a plain
        string (``"command": "/function ns:menu"``). Nothing else in this plugin sees those:
        :meth:`analyze_function_calls` only scans mcfunction bodies. Without this pass, a function
        reachable *only* from a dialog button is reported as an orphan (``@within ???``), which is
        actively misleading — it looks like dead code.

        The dialog is scanned as **serialized text**, never through ``.data``: reading ``.data``
        calls beet's ``ensure_deserialized()``, which replaces the file's stored content with the
        parsed form, so the dialog would then be re-encoded on output and lose its original
        formatting. ``.text`` goes through the file's own encoder — the same one used to write it —
        so analysis stays read-only. Scanning the whole serialized dialog also means this does not
        need to know where in the dialog schema a command may appear.

        Examples:
            >>> from types import SimpleNamespace
            >>> dialog = SimpleNamespace(
            ...     text='{"actions":[{"action":{"type":"run_command","command":"/function test:menu"}}]}'
            ... )
            >>> ctx = SimpleNamespace(data=SimpleNamespace(dialogs={"test:config": dialog}))
            >>> menu = Header("test:menu", [], [], "")
            >>> FunctionAnalyzer(ctx, {"test:menu": menu}).analyze_dialogs()  # type: ignore[arg-type]
            >>> menu.within
            ['dialog test:config']

            A dialog that references no function leaves every header untouched:
            >>> dialog = SimpleNamespace(text='{"type":"minecraft:notice","title":"hi"}')
            >>> ctx = SimpleNamespace(data=SimpleNamespace(dialogs={"test:notice": dialog}))
            >>> menu = Header("test:menu", [], [], "")
            >>> FunctionAnalyzer(ctx, {"test:menu": menu}).analyze_dialogs()  # type: ignore[arg-type]
            >>> menu.within
            []

            The same function referenced by two buttons is only listed once:
            >>> dialog = SimpleNamespace(text='["/function test:menu", "/function test:menu"]')
            >>> ctx = SimpleNamespace(data=SimpleNamespace(dialogs={"test:config": dialog}))
            >>> menu = Header("test:menu", [], [], "")
            >>> FunctionAnalyzer(ctx, {"test:menu": menu}).analyze_dialogs()  # type: ignore[arg-type]
            >>> menu.within
            ['dialog test:config']
        """
        for dialog_path, dialog in self.ctx.data.dialogs.items():
            # Mirrors the "advancement <path>" convention used by analyze_advancements
            to_be_called: str = f"dialog {dialog_path}"
            for match in FUNCTION_CALL_RE.finditer(dialog.text):
                called: str = match.group(1)
                if called in self.mcfunctions and to_be_called not in self.mcfunctions[called].within:
                    self.mcfunctions[called].within.append(to_be_called)

    def analyze_function_calls(self) -> None:
        """ Analyze function calls within mcfunction files.

        Examples:
            Detecting nested function references inside macro payloads:
            >>> caller = Header(
            ...     "test:caller",
            ...     [],
            ...     [],
            ...     'function #bs.raycast:run {with: {on_exit_point: "function test:earth/on_exit"}}',
            ... )
            >>> raycast = Header("#bs.raycast:run", [], [], "")
            >>> exit_fn = Header("test:earth/on_exit", [], [], "")
            >>> mcfunctions = {
            ...     "test:caller": caller,
            ...     "#bs.raycast:run": raycast,
            ...     "test:earth/on_exit": exit_fn,
            ... }
            >>> analyzer = FunctionAnalyzer(None, mcfunctions)  # type: ignore[arg-type]
            >>> analyzer.analyze_function_calls()
            >>> any(item.startswith("test:caller") for item in mcfunctions["test:earth/on_exit"].within)
            True

            A function name that only appears inside a tellraw suggest_command is recorded as a
            "string in <caller>" reference (mirroring the "advancement <path>" convention), without
            dragging the surrounding JSON into the header as macro data:
            >>> caller = Header(
            ...     "test:menu",
            ...     [],
            ...     [],
            ...     'tellraw @a [{"text":"[Restart]","click_event":{"action":"suggest_command","command":"/function test:restart"}}]',
            ... )
            >>> restart = Header("test:restart", [], [], "")
            >>> mcfunctions = {"test:menu": caller, "test:restart": restart}
            >>> analyzer = FunctionAnalyzer(None, mcfunctions)  # type: ignore[arg-type]
            >>> analyzer.analyze_function_calls()
            >>> mcfunctions["test:restart"].within
            ['string in test:menu']

            A macro function call (leading "$") is a real command call, not a string reference:
            >>> caller = Header("test:caller", [], [], '$function test:target {slot:"$(slot)"}')
            >>> target = Header("test:target", [], [], "")
            >>> mcfunctions = {"test:caller": caller, "test:target": target}
            >>> analyzer = FunctionAnalyzer(None, mcfunctions)  # type: ignore[arg-type]
            >>> analyzer.analyze_function_calls()
            >>> mcfunctions["test:target"].within
            ['test:caller {slot:"$(slot)"}']
        """
        # For each mcfunction file, look at each line
        for path, header in self.mcfunctions.items():
            for line in header.content.split("\n"):

                # Skip lines with no function reference at all
                if "function " not in line:
                    continue

                # A real command call anchors "function" at the command start or after run/schedule,
                # AND is not inside a quoted argument string (a dialog button's
                # command:"/execute ... run function ns:foo" also contains "run function").
                # Its payload (macros / schedule time) and execution context only apply to THAT call.
                command_match = next(
                    (m for m in COMMAND_CALL_RE.finditer(line) if not self.is_inside_string(line, m.start())),
                    None,
                )
                if command_match is not None:
                    primary: str = command_match.group(2)

                    # Everything after the called function is macro data ({...}) or a schedule time
                    more_text: str = line[command_match.end():].replace("\n", "").strip()
                    more: str = f" {more_text}" if more_text else ""

                    # "schedule function ..." loses execution context (it runs on a later tick)
                    is_scheduled: bool = command_match.group("sched") is not None
                    line_context: str | None = None if is_scheduled else parse_execution_context_from_line(line)

                    # Create the caller string with context if available
                    caller_info: str = path + more
                    if line_context:
                        line_context = "".join(
                            x for i, x in enumerate(line_context)
                            if x != " " or (i > 0 and line_context[i - 1] not in ":,")
                        )
                        caller_info += f" [ {line_context} ]"
                    elif is_scheduled:
                        # Mark scheduled calls with a special marker so context analyzer knows not to inherit context
                        caller_info += " [ scheduled ]"

                    # The primary call plus any nested references inside its macro payload (e.g.
                    # function #tag:run {with: {on_exit_point: "function ns:path"}}) share this caller info.
                    called_functions: list[str] = [primary]
                    for match in FUNCTION_CALL_RE.finditer(line):
                        candidate: str = match.group(1)
                        if candidate not in called_functions:
                            called_functions.append(candidate)
                    for called in called_functions:
                        if called in self.mcfunctions and caller_info not in self.mcfunctions[called].within:
                            self.mcfunctions[called].within.append(caller_info)

                # No real command call: the reference lives inside an argument string (tellraw
                # suggest_command/run_command, etc.). Record it as "string in <caller>", mirroring the
                # "advancement <path>" convention, so the header shows it is only a string reference.
                # The "string" prefix also keeps the context analyzer from inheriting the caller's
                # execution context — a clicked chat command runs as the player, not in that context.
                else:
                    for match in FUNCTION_CALL_RE.finditer(line):
                        candidate = match.group(1)
                        caller_ref: str = f"string in {path}"
                        if candidate in self.mcfunctions and caller_ref not in self.mcfunctions[candidate].within:
                            self.mcfunctions[candidate].within.append(caller_ref)

    def analyze_all_relationships(self) -> None:
        """ Analyze all function relationships. """
        self.analyze_function_tags()
        self.analyze_advancements()
        self.analyze_function_calls()
        self.analyze_dialogs()  # Last: ContextAnalyzer takes the FIRST caller, so mcfunction callers keep priority

    @staticmethod
    def is_inside_string(line: str, pos: int) -> bool:
        """ Return whether character index ``pos`` in ``line`` sits inside a double-quoted string.

        Counts unescaped double quotes before ``pos``; an odd count means an unclosed string is open.

        Args:
            line (str): The line to scan.
            pos  (int): The character index whose string-membership is tested.

        Examples:
            >>> FunctionAnalyzer.is_inside_string('run function a:b', 4)
            False
            >>> FunctionAnalyzer.is_inside_string('command:"/execute run function a:b"', 26)
            True
            >>> FunctionAnalyzer.is_inside_string('data set value {a:"x"} run function a:b', 30)
            False
        """
        # Without a single backslash there is nothing to escape, so counting quotes is exact
        prefix: str = line[:pos]
        if "\\" not in prefix:
            return prefix.count('"') % 2 == 1

        quotes: int = 0
        i: int = 0
        while i < pos and i < len(line):
            char: str = line[i]
            if char == "\\":
                i += 2  # Skip the escaped character
                continue
            if char == '"':
                quotes += 1
            i += 1
        return quotes % 2 == 1

