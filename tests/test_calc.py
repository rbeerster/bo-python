import unittest
import math
import datetime

import blitzortung

class ThreePointSolutionTest(unittest.TestCase):

    def setUp(self):
        self.timestamp = datetime.datetime.utcnow()
        event_builder = blitzortung.builder.Event()
        event_builder.set_x(11.0)
        event_builder.set_y(49.0)
        event_builder.set_timestamp(self.timestamp)
        self.center_event = event_builder.build()    
        self.radians_factor = math.pi / 180

    def test_get_solution_location(self):
        solution = blitzortung.calc.ThreePointSolution(self.center_event, 0, 100000)
        location = solution.get_location()

        self.assertAlmostEqual(location.get_x(), 11)
        self.assertAlmostEqual(location.get_y(), 49.89913151)

        solution = blitzortung.calc.ThreePointSolution(self.center_event, math.pi / 2, 100000)
        location = solution.get_location()

        self.assertAlmostEqual(location.get_x(), 12.3664992)
        self.assertAlmostEqual(location.get_y(), 48.9919072)    

    def test_get_solution_timestamp(self):
        solution = blitzortung.calc.ThreePointSolution(self.center_event, 0, 100000)

class ThreePointSolverTest(unittest.TestCase):

    def setUp(self):
        self.signal_velocity = blitzortung.calc.SignalVelocity()
        self.prepare_solution(blitzortung.types.Point(11.5, 49.5))
        
    def prepare_solution(self, location):
        location_0 = blitzortung.types.Point(11.0, 49.0)
        location_1 = blitzortung.types.Point(12.0, 49.0)
        location_2 = blitzortung.types.Point(11.0, 50.0)
        
        distance_0 = location.distance_to(location_0)
        ns_offset_0 = self.signal_velocity.get_distance_time(distance_0)
        distance_1 = location.distance_to(location_1)
        ns_offset_1 = self.signal_velocity.get_distance_time(distance_1)
        distance_2 = location.distance_to(location_2)
        ns_offset_2 = self.signal_velocity.get_distance_time(distance_2)
        
        #print "azimuth: ", location_0.azimuth_to(location) / math.pi * 180
        
        self.timestamp = datetime.datetime.utcnow()
        event_builder = blitzortung.builder.Event()
        
        #print "ns offsets:", ns_offset_0, ns_offset_1, ns_offset_2
        
        event_builder.set_x(location_0.get_x())
        event_builder.set_y(location_0.get_y())
        event_builder.set_timestamp(self.timestamp, ns_offset_0)
        self.center_event = event_builder.build()
        
        event_builder.set_x(location_1.get_x())
        event_builder.set_y(location_1.get_y())
        event_builder.set_timestamp(self.timestamp, ns_offset_1)
        self.event_1 = event_builder.build()
        
        event_builder.set_x(location_2.get_x())
        event_builder.set_y(location_2.get_y())
        event_builder.set_timestamp(self.timestamp, ns_offset_2)
        self.event_2 = event_builder.build()
        
        self.events = [self.center_event, self.event_1, self.event_2]
        
    def test_solve_with_one_solution(self):
        
        location = blitzortung.types.Point(11.7, 49.3)
        self.prepare_solution(location)
        
        solver = blitzortung.calc.ThreePointSolver(self.events)
        
        solutions = solver.get_solutions()
        
        self.assertEqual(1, len(solutions))
        
        self.assertEqual(location, solutions[0].get_location())
        
            
    def test_solve_with_two_solutions(self):
        
        location = blitzortung.types.Point(11.1, 49.1)
        self.prepare_solution(location)
        
        solver = blitzortung.calc.ThreePointSolver(self.events)
        
        solutions = solver.get_solutions()
        
        self.assertEqual(2, len(solutions))
        
        self.assertEqual(location, solutions[0].get_location())
        
        self.assertNotEqual(location, solutions[1].get_location())
            
    def test_azimuth_to_angle(self):
        solver = blitzortung.calc.ThreePointSolver(self.events)
                
        self.assertAlmostEqual(math.pi / 2, solver.azimuth_to_angle(0))
        self.assertAlmostEqual(0, solver.azimuth_to_angle(math.pi / 2))
        self.assertAlmostEqual(math.pi, solver.azimuth_to_angle(-math.pi / 2))
        
    def test_angle_to_azimuth(self):
        solver = blitzortung.calc.ThreePointSolver(self.events)
                
        self.assertAlmostEqual(math.pi / 2, solver.angle_to_azimuth(0))
        self.assertAlmostEqual(0, solver.angle_to_azimuth(math.pi / 2))
        self.assertAlmostEqual(-math.pi / 2, solver.angle_to_azimuth(math.pi))
        
        