""" Model elements of custom block displays: grown a little, turned, flipped or cut into stairs corners, keeping the world grid. """
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import math

from stouputils.typing import JsonDict, JsonList

# Constants
DIRECTIONS: dict[str, tuple[int, int, int]] = {
	"north": (0, 0, -1), "south": (0, 0, 1), "east": (1, 0, 0), "west": (-1, 0, 0), "up": (0, 1, 0), "down": (0, -1, 0),
}

CUBE_ELEMENT: JsonDict = {
	"from": [0, 0, 0], "to": [16, 16, 16],
	"faces": {direction: {"texture": f"#{direction}", "cullface": direction} for direction in DIRECTIONS},
}
""" The element of `block/cube`, which every cube shaped vanilla model inherits. """

UVLOCK_TURNS: dict[int, int] = {2: 90, 3: 180, 4: 270}
""" Degrees about Y of the model copy shown for each `#rotation` score, 1 (a placer looking south) showing the model itself. """

CUBE_PARENTS: tuple[str, ...] = (
	"block/cube", "block/cube_all", "block/cube_bottom_top", "block/cube_column", "block/orientable", "block/orientable_with_bottom",
)
""" Vanilla models drawing `CUBE_ELEMENT`, without their optional "minecraft:" namespace. """


# Functions
def cake_element(bites: int) -> JsonDict:
	""" The element of `block/cake` (0 bites) or `block/cake_slice<bites>`.

	>>> cake_element(2)["from"], cake_element(2)["faces"]["west"]
	([5, 0, 1], {'texture': '#inside'})
	"""
	return {"from": [1 + 2 * bites, 0, 1], "to": [15, 8, 15], "faces": {
		"down": {"texture": "#bottom", "cullface": "down"}, "up": {"texture": "#top"},
		"north": {"texture": "#side"}, "south": {"texture": "#side"},
		"west": {"texture": "#inside" if bites else "#side"}, "east": {"texture": "#side"},
	}}


def vanilla_elements(parent: str) -> JsonList | None:
	""" The elements a vanilla parent model draws, None when it is not one of the cube or cake models.

	>>> vanilla_elements("minecraft:block/cube_all") == [CUBE_ELEMENT], vanilla_elements("block/stairs")
	(True, None)
	"""
	path: str = parent.removeprefix("minecraft:")
	if path in CUBE_PARENTS:
		return [CUBE_ELEMENT]
	if path == "block/cake":
		return [cake_element(0)]
	if path.startswith("block/cake_slice"):
		return [cake_element(int(path.removeprefix("block/cake_slice")))]
	return None


def with_margin(element: JsonDict, scale: float) -> JsonDict:
	""" The element scaled by `scale` about its own center, so none of its faces lies on a face of the host block.

	Each face keeps the UVs its original size gave it: the game would read UVs past the texture's edges from the grown size.

	>>> faces = {"north": {"texture": "#side"}, "up": {"uv": [0, 0, 1, 1]}}
	>>> element = with_margin({"from": [0, 0, 6], "to": [16, 8, 10], "faces": faces}, 1.25)
	>>> element["from"], element["to"], element["faces"]["north"]["uv"], element["faces"]["up"]["uv"]
	([-2.0, -1.0, 5.5], [18.0, 9.0, 10.5], [0, 8, 16, 16], [0, 0, 1, 1])
	"""
	(x1, y1, z1), (x2, y2, z2) = element["from"], element["to"]
	default_uvs: dict[str, list[float]] = {
		"down": [x1, 16 - z2, x2, 16 - z1], "up": [x1, z1, x2, z2],
		"north": [16 - x2, 16 - y2, 16 - x1, 16 - y1], "south": [x1, 16 - y2, x2, 16 - y1],
		"west": [z1, 16 - y2, z2, 16 - y1], "east": [16 - z2, 16 - y2, 16 - z1, 16 - y1],
	}
	center: list[float] = [(low + high) / 2 for low, high in zip(element["from"], element["to"], strict=True)]
	return {
		**element,
		"from": [c + (low - c) * scale for c, low in zip(center, element["from"], strict=True)],
		"to": [c + (high - c) * scale for c, high in zip(center, element["to"], strict=True)],
		"faces": {direction: {"uv": default_uvs[direction], **face} for direction, face in element["faces"].items()},
	}


def model_with_margin(model: JsonDict, scale: float) -> JsonDict:
	""" The model with each of its own elements scaled by `with_margin`, unchanged when it has none. """
	return {**model, "elements": [with_margin(element, scale) for element in model["elements"]]} if "elements" in model else model


def flipped(element: JsonDict) -> JsonDict:
	""" A box element mirrored about the horizontal plane through the block center, as a block placed on the upper half is.

	Its faces lose their UVs, so they map the texture from the world grid.

	>>> faces = {"up": {"texture": "#top", "cullface": "up"}, "down": {"texture": "#bottom"}, "north": {"uv": [0, 8, 16, 16]}}
	>>> element = flipped({"from": [0, 0, 0], "to": [16, 8, 16], "faces": faces})
	>>> element["from"], element["to"], element["faces"]
	([0, 8, 0], [16, 16, 16], {'down': {'texture': '#top', 'cullface': 'down'}, 'up': {'texture': '#bottom'}, 'north': {}})
	"""
	(x1, y1, z1), (x2, y2, z2) = element["from"], element["to"]
	swapped: dict[str, str] = {"up": "down", "down": "up"}
	faces: JsonDict = {
		swapped.get(str(direction), str(direction)): {
			key: swapped.get(str(value), str(value)) if key == "cullface" else value
			for key, value in face.items() if key not in ("uv", "rotation")
		}
		for direction, face in element["faces"].items()
	}
	return {**element, "from": [x1, 16 - y2, z1], "to": [x2, 16 - y1, z2], "faces": faces}


def stairs_corner(elements: JsonList, shape: str) -> JsonList:
	""" The elements of a stairs corner, from those of straight stairs facing south, its faces mapping the texture from the world grid.

	An inner corner adds the stairs turned a quarter towards its side, an outer corner keeps what both have in common.

	>>> faces = {"up": {"texture": "#t", "uv": [0, 0, 16, 16]}}
	>>> straight = [{"from": [0, 0, 0], "to": [16, 8, 16], "faces": faces}, {"from": [0, 8, 8], "to": [16, 16, 16], "faces": faces}]
	>>> [(e["from"], e["to"]) for e in stairs_corner(straight, "outer_right")]
	[([0, 0, 0], [16, 8, 16]), ([0, 8, 8], [8.0, 16, 16])]
	>>> [(e["from"], e["to"]) for e in stairs_corner(straight, "inner_left")][2:]
	[([8.0, 8.0, 0.0], [16.0, 16.0, 16.0])]
	"""
	turned_elements: JsonList = [uv_locked(element, 0, 90 if shape.endswith("right") else 270) for element in elements]
	if shape.startswith("inner"):
		boxes: list[tuple[list[float], list[float]]] = [(element["from"], element["to"]) for element in elements]
		return [*elements, *(element for element in turned_elements if (element["from"], element["to"]) not in boxes)]
	return [common for element in elements for other in turned_elements if (common := overlap(element, other))]


def overlap(element: JsonDict, other: JsonDict) -> JsonDict | None:
	""" The part of a box element inside another, its faces without UVs, None when they do not overlap. """
	low: list[float] = [max(a, b) for a, b in zip(element["from"], other["from"], strict=True)]
	high: list[float] = [min(a, b) for a, b in zip(element["to"], other["to"], strict=True)]
	if any(a >= b for a, b in zip(low, high, strict=True)):
		return None
	faces: JsonDict = {
		direction: {key: value for key, value in face.items() if key not in ("uv", "rotation")}
		for direction, face in element["faces"].items()
	}
	return {**element, "from": low, "to": high, "faces": faces}


def turned(vector: tuple[float, float, float], x: int, y: int) -> tuple[float, float, float]:
	""" A vector turned as a blockstate turns its model.

	It turns `x` degrees about the X axis, then `y` about the Y axis, clockwise seen from the positive side.

	>>> turned((0, 0, -1), 0, 90), turned((0, 1, 0), 180, 0)
	((1.0, 0.0, 0.0), (0.0, -1.0, 0.0))
	"""
	vx, vy, vz = vector
	ax, ay = math.radians(-x), math.radians(-y)
	vy, vz = vy * math.cos(ax) - vz * math.sin(ax), vy * math.sin(ax) + vz * math.cos(ax)
	vx, vz = vx * math.cos(ay) + vz * math.sin(ay), -vx * math.sin(ay) + vz * math.cos(ay)
	return (round(vx, 6) + 0.0, round(vy, 6) + 0.0, round(vz, 6) + 0.0)


def uv_locked(element: JsonDict, x: int, y: int) -> JsonDict:
	""" A box element turned about the block center.

	Its faces lose their UVs, so they map the texture from the world grid as `uvlock` does.

	>>> faces = {"north": {"uv": [0, 8, 16, 16], "texture": "#side"}}
	>>> element = uv_locked({"from": [0, 0, 0], "to": [16, 8, 8], "faces": faces}, 0, 90)
	>>> element["from"], element["to"], element["faces"]
	([8.0, 0.0, 0.0], [16.0, 8.0, 16.0], {'east': {'texture': '#side'}})
	"""
	corners = [turned((px - 8, py - 8, pz - 8), x, y) for px, py, pz in (element["from"], element["to"])]
	faces: JsonDict = {
		next(name for name, vector in DIRECTIONS.items() if vector == turned(DIRECTIONS[direction], x, y)):
		{key: value for key, value in face.items() if key not in ("uv", "rotation")}
		for direction, face in element["faces"].items()
	}
	return {
		**element, "faces": faces,
		"from": [min(a, b) + 8 for a, b in zip(*corners, strict=True)], "to": [max(a, b) + 8 for a, b in zip(*corners, strict=True)],
	}

