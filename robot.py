from __future__ import print_function
import unittest
from collections import namedtuple

NORTH = "N"
WEST = "W"
EAST = "E"
SOUTH = "S"

TURN = 'turn'
GO = 'go'
START = 'start'


def apply_turn(position, instaction):
    """Apply turn instaction logic to current position
    Args:
        position: (Position) current robot position
        instaction: (dict) instruction to apply
    Returns:
        (Position) newly calculated position
    """
    directions = [NORTH, EAST, SOUTH, WEST]
    current_direction = position.direction
    turn_direction = instaction['direction']

    direction_index = directions.index(current_direction)
    if turn_direction == 'left':
        direction_index = (direction_index - 1) % len(directions)
    if turn_direction == 'right':
        direction_index = (direction_index + 1) % len(directions)

    print('Turned to', directions[direction_index])
    return position._replace(direction=directions[direction_index])


def apply_go(position, instaction):
    """Apply go instaction logic to current position
    Args:
        position: (Position) current robot position
        instaction: (dict) instruction to apply
    Returns:
        (Position) newly calculated position
    """

    direction = instaction.get('direction', position.direction)
    distance = instaction.get('distance')

    print("Followed {} {} blocks".format(direction, distance))

    if direction == NORTH:
        return position._replace(y=position.y + distance, direction=direction)
    elif direction == SOUTH:
        return position._replace(y=position.y - distance, direction=direction)
    elif direction == EAST:
        return position._replace(x=position.x + distance, direction=direction)
    elif direction == WEST:
        return position._replace(x=position.x - distance, direction=direction)

    return position


def apply_start(position, instaction):
    """Apply start instaction logic to current position
    Args:
        position: (Position) current robot position
        instaction: (dict) instruction to apply
    Returns:
        (Position) newly calculated position
    """

    x, y = instaction['position']

    print('Started the route')

    return Position(x, y, NORTH)


INSTRUCTION_APPLY_MAP = {
    TURN: apply_turn,
    GO: apply_go,
    START: apply_start,
}


Position = namedtuple('Position', ('x', 'y', 'direction'))


class NoStartInstrunction(Exception):
    """Start instruction was not found at the start of instructions list."""
    pass


class Robot(object):
    """Robot class
    Args:
        route_requester: (func) Request route to follow
    """
    def __init__(self, route_requester):
        self.position = None
        self.route_requester = route_requester

    def follow_route(self):
        route = self.route_requester()
        instructions = route['instructions']

        if instructions[0]['type'] is not START:
            raise NoStartInstrunction

        print('Follow route: {}'.format(route['title']))

        for instruction in instructions:
            self.position = INSTRUCTION_APPLY_MAP[instruction['type']](self.position, instruction)

            print('At position: ', self.position)


class InstructionsTestCase(unittest.TestCase):
    def test_apply_start(self):
        position = None
        instruction = {"type": "start", "position": [555, 600]}
        self.assertEqual(INSTRUCTION_APPLY_MAP['start'](position, instruction), Position(555, 600, NORTH))

        position = Position(10, 20, NORTH)
        instruction = {"type": "start", "position": [555, 600]}
        self.assertEqual(INSTRUCTION_APPLY_MAP['start'](position, instruction), Position(555, 600, NORTH))

    def test_apply_turn_right(self):
        position = Position(0, 0, NORTH)
        instruction = {"type": "turn", "direction": "right"}

        next_position = INSTRUCTION_APPLY_MAP['turn'](position, instruction)
        self.assertEqual(next_position, Position(0, 0, EAST))

        next_position = INSTRUCTION_APPLY_MAP['turn'](next_position, instruction)
        self.assertEqual(next_position, Position(0, 0, SOUTH))

        next_position = INSTRUCTION_APPLY_MAP['turn'](next_position, instruction)
        self.assertEqual(next_position, Position(0, 0, WEST))

        next_position = INSTRUCTION_APPLY_MAP['turn'](next_position, instruction)
        self.assertEqual(next_position, Position(0, 0, NORTH))

    def test_apply_turn_left(self):
        position = Position(0, 0, NORTH)
        instruction = {"type": "turn", "direction": "left"}

        next_position = INSTRUCTION_APPLY_MAP['turn'](position, instruction)
        self.assertEqual(next_position, Position(0, 0, WEST))

        next_position = INSTRUCTION_APPLY_MAP['turn'](next_position, instruction)
        self.assertEqual(next_position, Position(0, 0, SOUTH))

        next_position = INSTRUCTION_APPLY_MAP['turn'](next_position, instruction)
        self.assertEqual(next_position, Position(0, 0, EAST))

        next_position = INSTRUCTION_APPLY_MAP['turn'](next_position, instruction)
        self.assertEqual(next_position, Position(0, 0, NORTH))

    def test_go_distance(self):
        instruction = {"type": "go", "distance": 10}

        position = Position(100, 100, NORTH)
        next_position = INSTRUCTION_APPLY_MAP['go'](position, instruction)
        self.assertEqual(next_position, Position(100, 110, NORTH))

        position = Position(100, 100, SOUTH)
        next_position = INSTRUCTION_APPLY_MAP['go'](position, instruction)
        self.assertEqual(next_position, Position(100, 90, SOUTH))

        position = Position(100, 100, EAST)
        next_position = INSTRUCTION_APPLY_MAP['go'](position, instruction)
        self.assertEqual(next_position, Position(110, 100, EAST))

        position = Position(100, 100, WEST)
        next_position = INSTRUCTION_APPLY_MAP['go'](position, instruction)
        self.assertEqual(next_position, Position(90, 100, WEST))

    def test_go_distance_with_direction(self):
        position = Position(100, 100, NORTH)

        instruction = {"type": "go", "distance": 10, "direction": NORTH}
        next_position = INSTRUCTION_APPLY_MAP['go'](position, instruction)
        self.assertEqual(next_position, Position(100, 110, NORTH))

        instruction = {"type": "go", "distance": 10, "direction": SOUTH}
        next_position = INSTRUCTION_APPLY_MAP['go'](position, instruction)
        self.assertEqual(next_position, Position(100, 90, SOUTH))

        instruction = {"type": "go", "distance": 10, "direction": EAST}
        next_position = INSTRUCTION_APPLY_MAP['go'](position, instruction)
        self.assertEqual(next_position, Position(110, 100, EAST))

        instruction = {"type": "go", "distance": 10, "direction": WEST}
        next_position = INSTRUCTION_APPLY_MAP['go'](position, instruction)
        self.assertEqual(next_position, Position(90, 100, WEST))


class RobotTestCase(unittest.TestCase):
    def test_first_instruction_is_not_start(self):
        def route_requester(*args, **kwargs):
            return {
                "title": "To the airport",
                "instructions": [
                    {
                        "type": "go",
                        "distance": 12,
                        "direction": "E"
                    }
                ]
            }

        robot = Robot(route_requester)
        with self.assertRaises(NoStartInstrunction):
            robot.follow_route()

    def test_follow_route(self):
        def route_requester(*args, **kwargs):
            return {
                "title": "To the airport",
                "instructions": [
                    {
                        "type": "start",
                        "position": [
                            500,
                            600
                        ]
                    },
                    {
                        "type": "go",
                        "distance": 10,
                        "direction": "E"
                    },
                    {
                        "type": "turn",
                        "direction": "right"
                    },
                    {
                        "type": "go",
                        "distance": 20
                    }
                ]
            }

        robot = Robot(route_requester)
        robot.follow_route()
        self.assertEqual(robot.position, Position(510, 580, SOUTH))


if __name__ == '__main__':
    unittest.main()
