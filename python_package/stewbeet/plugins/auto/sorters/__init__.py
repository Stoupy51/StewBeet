from stouputils.decorators import measure_time
from stouputils.print import progress
from copy import deepcopy
from typing import Any, ClassVar, Literal, Type, TypeAlias
from pydantic.v1 import BaseModel
from beet import Context, FileDeserialize, Function, FunctionTag, JsonFileBase, NamespaceFileScope

SorterAlgorithm: TypeAlias = Literal[
    "quicksort"
]

class Sorter(BaseModel): 
    algorithm: SorterAlgorithm = "quicksort"
    """Algorithm used to sort the elements, defaults to `quicksort`."""
    directory: str
    """Namespaced id where the sorting functions are generated."""
    to_sort: dict[str, str]
    """Location of the list to sort."""
    key: str
    """The key to the number getting compared."""
    scale: int = 1
    """(Option) By how many the number should be scaled before getting rounded."""

class SorterFile(JsonFileBase[Sorter]):
    model: Type[Any] = Sorter
    scope: ClassVar[NamespaceFileScope] = ("sorter",)
    extension: ClassVar[str] = ".json"
    data: ClassVar[FileDeserialize[Sorter]] = FileDeserialize()

def generate_quicksort(ctx: Context, sorter: dict) -> None:
    """Some documentation goes here"""
    
    directory: str = sorter["directory"]
    macro: str = f'storage sorter:temp args'
    to_sort: str = f'storage {sorter["to_sort"]["storage"]} {sorter["to_sort"]["target"]}'
    key: str = sorter["key"]
    scale: int = sorter["scale"]

    sort: list[str] = [
        f'execute store result score high sorter.val run data get {to_sort}',
        f'execute store result {macro}.high int 1 run scoreboard players remove high sorter.val 1',
        f'data modify {macro}.low set value 0',
        f'function {directory}/0 with {macro}'
    ]

    quicksort: list[str] = [
        '$execute if predicate {"condition": "value_check","range": {"min": -8,"max": $(low)},"value": $(high)} run return 0',
        '$execute store result score pi sorter.val run function ' + directory + '/1 {low:$(low),high:$(high)}',
        'data modify storage sorter:temp inInt append value 0',
        f'execute store result storage sorter:temp inInt[-1] int 1 store result {macro}.high int 1 run scoreboard players remove pi sorter.val 1',
        f'function {directory}/0 with {macro}',
        'execute store result score pi sorter.val run data get storage sorter:temp inInt[-1]',
        f'execute store result {macro}.low int 1 run scoreboard players add pi sorter.val 2',
        f'$data modify {macro}.high set value $(high)',
        f'function {directory}/0 with {macro}'
    ]

    partition: list[str] = [
        f'$execute store result score pivot sorter.val run data get {to_sort}[$(high)].{key} {scale}',
        '$scoreboard players set i sorter.val $(low)',
        'scoreboard players remove i sorter.val 1',
        f'$execute store result {macro}.j int 1 run scoreboard players set j sorter.val $(low)',
        '$function ' + directory + '/2 {high:$(high),low:$(low),j:$(low)}',
        f'execute store result {macro}.i int 1 run scoreboard players add i sorter.val 1',
        f'$data modify {macro}.j set value $(high)',
        f'function {directory}/3 with {macro}',
        'return run scoreboard players get i sorter.val'
    ]

    partition_loop: list[str] = [
        '$execute if score j sorter.val matches $(high).. run return 0',
        f'$execute store result score test sorter.val run data get {to_sort}[$(j)].{key} {scale}',
        f'execute if score test sorter.val < pivot sorter.val run function {directory}/4 with {macro}',
        f'execute store result {macro}.j int 1 run scoreboard players add j sorter.val 1',
        f'function {directory}/2 with {macro}'
    ]

    partition_swap: list[str] = [
        f'$data modify storage sorter:temp element set from {to_sort}[$(i)]',
        f'$data modify {to_sort}[$(i)] set from {to_sort}[$(j)]',
        f'$data modify {to_sort}[$(j)] set from storage sorter:temp element'
    ]

    partition_loop_swap: list[str] = [
        f'execute store result {macro}.i int 1 run scoreboard players add i sorter.val 1',
        f'function {directory}/3 with {macro}'
    ]

    ctx.generate(f'{directory}/sort', Function(sort))
    ctx.generate(f'{directory}/0', Function(quicksort))
    ctx.generate(f'{directory}/1', Function(partition))
    ctx.generate(f'{directory}/2', Function(partition_loop))
    ctx.generate(f'{directory}/3', Function(partition_swap))
    ctx.generate(f'{directory}/4', Function(partition_loop_swap))

def generate_sorter(ctx: Context, sorter: dict):
    """Currently an unnecessary layer of abstraction in case more algorithms appear in the future."""
    match(sorter["algorithm"]):
        case "quicksort":
            generate_quicksort(ctx, sorter)

# Main entry point
@measure_time(progress, message="Execution time of 'stewbeet.plugins.auto.sorters'")
def beet_default(ctx: Context):
    """ Main entry point for the sorters plugin.
	This plugin generates functions that sort lists in storage.

	Args:
		ctx (Context): The beet context.
	"""
    # copy sorters registry
    sorters: list[tuple[str, Sorter]] = deepcopy(ctx.data[SorterFile].items())
    
    # iterate
    for resource_location, file_instance in sorters:
        sorter: dict[str, Any] = file_instance.data.dict()
        generate_sorter(ctx, sorter)
    
    # clear the registry
    ctx.data[SorterFile].clear()

    # setup scoreboard objective and storage in a load function
    ctx.generate("sorter:load", Function([
        'scoreboard objectives add sorter.val dummy',
        'data modify storage sorter:temp inInt set value [0]'
    ]))
    ctx.data.function_tags.setdefault("minecraft:load", FunctionTag()).add("sorter:load")


def extend_data_pack(ctx: Context):
    print("defining sorter resource")
    ctx.data.extend_namespace.append(SorterFile)
