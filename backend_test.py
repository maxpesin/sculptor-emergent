#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Workout Tracking App
Tests all backend endpoints with realistic workout data
"""

import requests
import json
import sys
from datetime import datetime
import uuid

# Get backend URL from environment
BACKEND_URL = "https://a06fb5c8-aadb-4be6-9a6c-0758eb7b20f0.preview.emergentagent.com/api"

class WorkoutAPITester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.created_resources = {
            'exercises': [],
            'splits': [],
            'sessions': []
        }
    
    def log_test(self, test_name, success, message, response_data=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message,
            'response_data': response_data
        })
    
    def test_health_check(self):
        """Test basic API health check"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    self.log_test("Health Check", True, f"API is responding: {data['message']}")
                    return True
                else:
                    self.log_test("Health Check", False, "API responded but missing message field")
                    return False
            else:
                self.log_test("Health Check", False, f"API returned status {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, f"Failed to connect to API: {str(e)}")
            return False
    
    def test_get_exercises(self):
        """Test GET /api/exercises - should return 42 predefined exercises"""
        try:
            response = self.session.get(f"{self.base_url}/exercises")
            if response.status_code == 200:
                exercises = response.json()
                if len(exercises) == 42:
                    self.log_test("Get All Exercises", True, f"Retrieved {len(exercises)} exercises as expected")
                    return exercises
                else:
                    self.log_test("Get All Exercises", False, f"Expected 42 exercises, got {len(exercises)}")
                    return exercises
            else:
                self.log_test("Get All Exercises", False, f"API returned status {response.status_code}")
                return None
        except Exception as e:
            self.log_test("Get All Exercises", False, f"Request failed: {str(e)}")
            return None
    
    def test_get_muscle_groups(self):
        """Test GET /api/muscle-groups - should return 6 muscle groups"""
        try:
            response = self.session.get(f"{self.base_url}/muscle-groups")
            if response.status_code == 200:
                muscle_groups = response.json()
                expected_groups = {"Arms", "Back", "Chest", "Core", "Legs", "Shoulders"}
                actual_groups = set(muscle_groups)
                
                if actual_groups == expected_groups:
                    self.log_test("Get Muscle Groups", True, f"Retrieved all 6 expected muscle groups: {sorted(muscle_groups)}")
                    return muscle_groups
                else:
                    missing = expected_groups - actual_groups
                    extra = actual_groups - expected_groups
                    msg = f"Muscle groups mismatch. Missing: {missing}, Extra: {extra}"
                    self.log_test("Get Muscle Groups", False, msg)
                    return muscle_groups
            else:
                self.log_test("Get Muscle Groups", False, f"API returned status {response.status_code}")
                return None
        except Exception as e:
            self.log_test("Get Muscle Groups", False, f"Request failed: {str(e)}")
            return None
    
    def test_filter_exercises_by_muscle_group(self):
        """Test GET /api/exercises?muscle_group=Chest"""
        try:
            response = self.session.get(f"{self.base_url}/exercises?muscle_group=Chest")
            if response.status_code == 200:
                chest_exercises = response.json()
                if len(chest_exercises) > 0:
                    # Verify all exercises are chest exercises
                    all_chest = all(ex['muscle_group'] == 'Chest' for ex in chest_exercises)
                    if all_chest:
                        self.log_test("Filter Exercises by Muscle Group", True, f"Retrieved {len(chest_exercises)} chest exercises")
                        return chest_exercises
                    else:
                        self.log_test("Filter Exercises by Muscle Group", False, "Some exercises don't belong to Chest muscle group")
                        return chest_exercises
                else:
                    self.log_test("Filter Exercises by Muscle Group", False, "No chest exercises found")
                    return None
            else:
                self.log_test("Filter Exercises by Muscle Group", False, f"API returned status {response.status_code}")
                return None
        except Exception as e:
            self.log_test("Filter Exercises by Muscle Group", False, f"Request failed: {str(e)}")
            return None
    
    def test_create_exercise(self):
        """Test POST /api/exercises - create a new exercise"""
        try:
            new_exercise = {
                "name": "Barbell Hip Thrust",
                "muscle_group": "Legs",
                "equipment": "Barbell",
                "instructions": "Sit with back against bench, barbell over hips, thrust up squeezing glutes"
            }
            
            response = self.session.post(f"{self.base_url}/exercises", json=new_exercise)
            if response.status_code == 200:
                created_exercise = response.json()
                if 'id' in created_exercise and created_exercise['name'] == new_exercise['name']:
                    self.created_resources['exercises'].append(created_exercise['id'])
                    self.log_test("Create Exercise", True, f"Created exercise: {created_exercise['name']}")
                    return created_exercise
                else:
                    self.log_test("Create Exercise", False, "Exercise created but response format incorrect")
                    return None
            else:
                self.log_test("Create Exercise", False, f"API returned status {response.status_code}")
                return None
        except Exception as e:
            self.log_test("Create Exercise", False, f"Request failed: {str(e)}")
            return None
    
    def test_get_exercise_by_id(self, exercise_id):
        """Test GET /api/exercises/{exercise_id}"""
        try:
            response = self.session.get(f"{self.base_url}/exercises/{exercise_id}")
            if response.status_code == 200:
                exercise = response.json()
                if exercise['id'] == exercise_id:
                    self.log_test("Get Exercise by ID", True, f"Retrieved exercise: {exercise['name']}")
                    return exercise
                else:
                    self.log_test("Get Exercise by ID", False, "Exercise ID mismatch in response")
                    return None
            elif response.status_code == 404:
                self.log_test("Get Exercise by ID", False, "Exercise not found (404)")
                return None
            else:
                self.log_test("Get Exercise by ID", False, f"API returned status {response.status_code}")
                return None
        except Exception as e:
            self.log_test("Get Exercise by ID", False, f"Request failed: {str(e)}")
            return None
    
    def test_get_workout_splits(self):
        """Test GET /api/splits - should be empty initially"""
        try:
            response = self.session.get(f"{self.base_url}/splits")
            if response.status_code == 200:
                splits = response.json()
                self.log_test("Get Workout Splits", True, f"Retrieved {len(splits)} workout splits")
                return splits
            else:
                self.log_test("Get Workout Splits", False, f"API returned status {response.status_code}")
                return None
        except Exception as e:
            self.log_test("Get Workout Splits", False, f"Request failed: {str(e)}")
            return None
    
    def test_create_workout_split(self):
        """Test POST /api/splits - create a new workout split"""
        try:
            new_split = {
                "name": "Mike's Push/Pull/Legs Split",
                "days_per_week": 3,
                "days": [
                    {
                        "day_number": 1,
                        "day_name": "Push Day",
                        "muscle_groups": ["Chest", "Shoulders", "Arms"],
                        "exercises": [],
                        "completed": False
                    },
                    {
                        "day_number": 2,
                        "day_name": "Pull Day",
                        "muscle_groups": ["Back", "Arms"],
                        "exercises": [],
                        "completed": False
                    },
                    {
                        "day_number": 3,
                        "day_name": "Leg Day",
                        "muscle_groups": ["Legs", "Core"],
                        "exercises": [],
                        "completed": False
                    }
                ]
            }
            
            response = self.session.post(f"{self.base_url}/splits", json=new_split)
            if response.status_code == 200:
                created_split = response.json()
                if 'id' in created_split and created_split['name'] == new_split['name']:
                    self.created_resources['splits'].append(created_split['id'])
                    self.log_test("Create Workout Split", True, f"Created split: {created_split['name']}")
                    return created_split
                else:
                    self.log_test("Create Workout Split", False, "Split created but response format incorrect")
                    return None
            else:
                self.log_test("Create Workout Split", False, f"API returned status {response.status_code}")
                return None
        except Exception as e:
            self.log_test("Create Workout Split", False, f"Request failed: {str(e)}")
            return None
    
    def test_get_workout_split_by_id(self, split_id):
        """Test GET /api/splits/{split_id}"""
        try:
            response = self.session.get(f"{self.base_url}/splits/{split_id}")
            if response.status_code == 200:
                split = response.json()
                if split['id'] == split_id:
                    self.log_test("Get Workout Split by ID", True, f"Retrieved split: {split['name']}")
                    return split
                else:
                    self.log_test("Get Workout Split by ID", False, "Split ID mismatch in response")
                    return None
            elif response.status_code == 404:
                self.log_test("Get Workout Split by ID", False, "Split not found (404)")
                return None
            else:
                self.log_test("Get Workout Split by ID", False, f"API returned status {response.status_code}")
                return None
        except Exception as e:
            self.log_test("Get Workout Split by ID", False, f"Request failed: {str(e)}")
            return None
    
    def test_update_workout_split(self, split_id):
        """Test PUT /api/splits/{split_id}"""
        try:
            updated_split = {
                "name": "Mike's Updated Push/Pull/Legs Split",
                "days_per_week": 3,
                "days": [
                    {
                        "day_number": 1,
                        "day_name": "Push Day (Updated)",
                        "muscle_groups": ["Chest", "Shoulders", "Arms"],
                        "exercises": [],
                        "completed": False
                    },
                    {
                        "day_number": 2,
                        "day_name": "Pull Day (Updated)",
                        "muscle_groups": ["Back", "Arms"],
                        "exercises": [],
                        "completed": False
                    },
                    {
                        "day_number": 3,
                        "day_name": "Leg Day (Updated)",
                        "muscle_groups": ["Legs", "Core"],
                        "exercises": [],
                        "completed": False
                    }
                ]
            }
            
            response = self.session.put(f"{self.base_url}/splits/{split_id}", json=updated_split)
            if response.status_code == 200:
                updated = response.json()
                if updated['name'] == updated_split['name']:
                    self.log_test("Update Workout Split", True, f"Updated split: {updated['name']}")
                    return updated
                else:
                    self.log_test("Update Workout Split", False, "Split updated but name not changed")
                    return None
            elif response.status_code == 404:
                self.log_test("Update Workout Split", False, "Split not found for update (404)")
                return None
            else:
                self.log_test("Update Workout Split", False, f"API returned status {response.status_code}")
                return None
        except Exception as e:
            self.log_test("Update Workout Split", False, f"Request failed: {str(e)}")
            return None
    
    def test_get_workout_templates(self):
        """Test GET /api/templates - should return 3 predefined templates"""
        try:
            response = self.session.get(f"{self.base_url}/templates")
            if response.status_code == 200:
                templates = response.json()
                expected_templates = {"push_pull_legs", "upper_lower", "full_body"}
                actual_templates = set(templates.keys())
                
                if actual_templates == expected_templates:
                    # Verify template structure
                    valid_structure = True
                    for template_name, template_data in templates.items():
                        if not all(key in template_data for key in ['name', 'days_per_week', 'days']):
                            valid_structure = False
                            break
                    
                    if valid_structure:
                        self.log_test("Get Workout Templates", True, f"Retrieved all 3 templates with correct structure")
                        return templates
                    else:
                        self.log_test("Get Workout Templates", False, "Templates missing required fields")
                        return templates
                else:
                    missing = expected_templates - actual_templates
                    extra = actual_templates - expected_templates
                    msg = f"Template mismatch. Missing: {missing}, Extra: {extra}"
                    self.log_test("Get Workout Templates", False, msg)
                    return templates
            else:
                self.log_test("Get Workout Templates", False, f"API returned status {response.status_code}")
                return None
        except Exception as e:
            self.log_test("Get Workout Templates", False, f"Request failed: {str(e)}")
            return None
    
    def test_get_workout_sessions(self):
        """Test GET /api/sessions - should be empty initially"""
        try:
            response = self.session.get(f"{self.base_url}/sessions")
            if response.status_code == 200:
                sessions = response.json()
                self.log_test("Get Workout Sessions", True, f"Retrieved {len(sessions)} workout sessions")
                return sessions
            else:
                self.log_test("Get Workout Sessions", False, f"API returned status {response.status_code}")
                return None
        except Exception as e:
            self.log_test("Get Workout Sessions", False, f"Request failed: {str(e)}")
            return None
    
    def test_create_workout_session(self, split_id):
        """Test POST /api/sessions - create a new workout session"""
        try:
            new_session = {
                "split_id": split_id,
                "day_number": 1,
                "exercises": [
                    {
                        "exercise_id": "bench-press-id",
                        "exercise_name": "Bench Press",
                        "sets": [
                            {"set_number": 1, "weight": 135.0, "reps": 10},
                            {"set_number": 2, "weight": 155.0, "reps": 8},
                            {"set_number": 3, "weight": 175.0, "reps": 6}
                        ]
                    },
                    {
                        "exercise_id": "incline-press-id",
                        "exercise_name": "Incline Dumbbell Press",
                        "sets": [
                            {"set_number": 1, "weight": 60.0, "reps": 12},
                            {"set_number": 2, "weight": 65.0, "reps": 10},
                            {"set_number": 3, "weight": 70.0, "reps": 8}
                        ]
                    }
                ]
            }
            
            response = self.session.post(f"{self.base_url}/sessions", json=new_session)
            if response.status_code == 200:
                created_session = response.json()
                if 'id' in created_session and created_session['split_id'] == split_id:
                    self.created_resources['sessions'].append(created_session['id'])
                    self.log_test("Create Workout Session", True, f"Created session with {len(created_session['exercises'])} exercises")
                    return created_session
                else:
                    self.log_test("Create Workout Session", False, "Session created but response format incorrect")
                    return None
            else:
                self.log_test("Create Workout Session", False, f"API returned status {response.status_code}")
                return None
        except Exception as e:
            self.log_test("Create Workout Session", False, f"Request failed: {str(e)}")
            return None
    
    def test_get_workout_session_by_id(self, session_id):
        """Test GET /api/sessions/{session_id}"""
        try:
            response = self.session.get(f"{self.base_url}/sessions/{session_id}")
            if response.status_code == 200:
                session = response.json()
                if session['id'] == session_id:
                    self.log_test("Get Workout Session by ID", True, f"Retrieved session with {len(session['exercises'])} exercises")
                    return session
                else:
                    self.log_test("Get Workout Session by ID", False, "Session ID mismatch in response")
                    return None
            elif response.status_code == 404:
                self.log_test("Get Workout Session by ID", False, "Session not found (404)")
                return None
            else:
                self.log_test("Get Workout Session by ID", False, f"API returned status {response.status_code}")
                return None
        except Exception as e:
            self.log_test("Get Workout Session by ID", False, f"Request failed: {str(e)}")
            return None
    
    def test_create_session_with_completion_tracking(self, split_id):
        """Test creating a session with completion tracking fields"""
        try:
            new_session = {
                "split_id": split_id,
                "day_number": 1,
                "exercises": [
                    {
                        "exercise_id": "bench-press-completion-test",
                        "exercise_name": "Bench Press",
                        "sets": [
                            {"set_number": 1, "weight": 135.0, "reps": 10}
                        ],
                        "completed_count": 0,
                        "target_completions": 3,
                        "is_archived": False
                    },
                    {
                        "exercise_id": "incline-press-completion-test",
                        "exercise_name": "Incline Dumbbell Press",
                        "sets": [
                            {"set_number": 1, "weight": 60.0, "reps": 12}
                        ],
                        "completed_count": 0,
                        "target_completions": 3,
                        "is_archived": False
                    }
                ]
            }
            
            response = self.session.post(f"{self.base_url}/sessions", json=new_session)
            if response.status_code == 200:
                created_session = response.json()
                if 'id' in created_session:
                    # Verify completion tracking fields are present
                    for exercise in created_session['exercises']:
                        if not all(field in exercise for field in ['completed_count', 'target_completions', 'is_archived']):
                            self.log_test("Create Session with Completion Tracking", False, "Missing completion tracking fields")
                            return None
                        if exercise['completed_count'] != 0 or exercise['target_completions'] != 3 or exercise['is_archived'] != False:
                            self.log_test("Create Session with Completion Tracking", False, "Incorrect default completion tracking values")
                            return None
                    
                    self.created_resources['sessions'].append(created_session['id'])
                    self.log_test("Create Session with Completion Tracking", True, f"Created session with completion tracking for {len(created_session['exercises'])} exercises")
                    return created_session
                else:
                    self.log_test("Create Session with Completion Tracking", False, "Session created but missing ID")
                    return None
            else:
                self.log_test("Create Session with Completion Tracking", False, f"API returned status {response.status_code}")
                return None
        except Exception as e:
            self.log_test("Create Session with Completion Tracking", False, f"Request failed: {str(e)}")
            return None
    
    def test_complete_exercise(self, session_id, exercise_id):
        """Test PATCH /api/sessions/{session_id}/exercises/{exercise_id}/complete"""
        try:
            response = self.session.patch(f"{self.base_url}/sessions/{session_id}/exercises/{exercise_id}/complete")
            if response.status_code == 200:
                result = response.json()
                expected_fields = ['message', 'exercise_id', 'completed_count', 'is_archived']
                if all(field in result for field in expected_fields):
                    if result['exercise_id'] == exercise_id:
                        self.log_test("Complete Exercise", True, f"Exercise completed. Count: {result['completed_count']}, Archived: {result['is_archived']}")
                        return result
                    else:
                        self.log_test("Complete Exercise", False, "Exercise ID mismatch in response")
                        return None
                else:
                    self.log_test("Complete Exercise", False, "Missing required fields in response")
                    return None
            elif response.status_code == 404:
                self.log_test("Complete Exercise", False, "Session or exercise not found (404)")
                return None
            else:
                self.log_test("Complete Exercise", False, f"API returned status {response.status_code}")
                return None
        except Exception as e:
            self.log_test("Complete Exercise", False, f"Request failed: {str(e)}")
            return None
    
    def test_reset_exercise_completion(self, session_id, exercise_id):
        """Test PATCH /api/sessions/{session_id}/exercises/{exercise_id}/reset"""
        try:
            response = self.session.patch(f"{self.base_url}/sessions/{session_id}/exercises/{exercise_id}/reset")
            if response.status_code == 200:
                result = response.json()
                expected_fields = ['message', 'exercise_id', 'completed_count', 'is_archived']
                if all(field in result for field in expected_fields):
                    if result['exercise_id'] == exercise_id and result['completed_count'] == 0 and result['is_archived'] == False:
                        self.log_test("Reset Exercise Completion", True, f"Exercise reset successfully. Count: {result['completed_count']}, Archived: {result['is_archived']}")
                        return result
                    else:
                        self.log_test("Reset Exercise Completion", False, "Exercise not properly reset")
                        return None
                else:
                    self.log_test("Reset Exercise Completion", False, "Missing required fields in response")
                    return None
            elif response.status_code == 404:
                self.log_test("Reset Exercise Completion", False, "Session or exercise not found (404)")
                return None
            else:
                self.log_test("Reset Exercise Completion", False, f"API returned status {response.status_code}")
                return None
        except Exception as e:
            self.log_test("Reset Exercise Completion", False, f"Request failed: {str(e)}")
            return None
    
    def test_completion_tracking_flow(self, split_id):
        """Test complete exercise completion tracking flow"""
        print("\n🎯 Testing Exercise Completion Tracking Flow...")
        
        # Create a session with completion tracking
        session = self.test_create_session_with_completion_tracking(split_id)
        if not session:
            return False
        
        session_id = session['id']
        exercise_id = session['exercises'][0]['exercise_id']  # Use first exercise
        
        # Test completing exercise multiple times until archived
        completion_results = []
        for i in range(1, 4):  # Complete 3 times (should archive on 3rd)
            result = self.test_complete_exercise(session_id, exercise_id)
            if result:
                completion_results.append(result)
                expected_archived = (i >= 3)  # Should be archived after 3rd completion
                if result['completed_count'] == i and result['is_archived'] == expected_archived:
                    self.log_test(f"Completion {i}/3", True, f"Correct completion count and archive status")
                else:
                    self.log_test(f"Completion {i}/3", False, f"Expected count {i}, archived {expected_archived}, got count {result['completed_count']}, archived {result['is_archived']}")
            else:
                self.log_test(f"Completion {i}/3", False, "Failed to complete exercise")
                return False
        
        # Verify final state - should be archived after 3 completions
        if completion_results and completion_results[-1]['is_archived']:
            self.log_test("Exercise Archiving", True, "Exercise correctly archived after 3 completions")
        else:
            self.log_test("Exercise Archiving", False, "Exercise not archived after 3 completions")
            return False
        
        # Test reset functionality
        reset_result = self.test_reset_exercise_completion(session_id, exercise_id)
        if reset_result:
            # Verify exercise can be completed again after reset
            post_reset_completion = self.test_complete_exercise(session_id, exercise_id)
            if post_reset_completion and post_reset_completion['completed_count'] == 1 and not post_reset_completion['is_archived']:
                self.log_test("Post-Reset Completion", True, "Exercise can be completed again after reset")
                return True
            else:
                self.log_test("Post-Reset Completion", False, "Exercise not working properly after reset")
                return False
        else:
            return False
    
    def test_delete_workout_split(self, split_id):
        """Test DELETE /api/splits/{split_id}"""
        try:
            response = self.session.delete(f"{self.base_url}/splits/{split_id}")
            if response.status_code == 200:
                result = response.json()
                if "message" in result:
                    self.log_test("Delete Workout Split", True, f"Deleted split successfully: {result['message']}")
                    return True
                else:
                    self.log_test("Delete Workout Split", False, "Split deleted but no confirmation message")
                    return False
            elif response.status_code == 404:
                self.log_test("Delete Workout Split", False, "Split not found for deletion (404)")
                return False
            else:
                self.log_test("Delete Workout Split", False, f"API returned status {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Delete Workout Split", False, f"Request failed: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🏋️ Starting Workout Tracking App Backend API Tests")
        print("=" * 60)
        
        # Test 1: Health Check
        if not self.test_health_check():
            print("❌ API is not responding. Stopping tests.")
            return False
        
        # Test 2: Exercise Database Management
        print("\n📋 Testing Exercise Database Management...")
        exercises = self.test_get_exercises()
        muscle_groups = self.test_get_muscle_groups()
        chest_exercises = self.test_filter_exercises_by_muscle_group()
        created_exercise = self.test_create_exercise()
        
        if created_exercise:
            self.test_get_exercise_by_id(created_exercise['id'])
        
        # Test 3: Workout Split Management
        print("\n💪 Testing Workout Split Management...")
        initial_splits = self.test_get_workout_splits()
        created_split = self.test_create_workout_split()
        
        if created_split:
            self.test_get_workout_split_by_id(created_split['id'])
            self.test_update_workout_split(created_split['id'])
        
        # Test 4: Template System
        print("\n📝 Testing Template System...")
        templates = self.test_get_workout_templates()
        
        # Test 5: Workout Session Management
        print("\n🏃 Testing Workout Session Management...")
        initial_sessions = self.test_get_workout_sessions()
        
        if created_split:
            created_session = self.test_create_workout_session(created_split['id'])
            if created_session:
                self.test_get_workout_session_by_id(created_session['id'])
        
        # Test 6: Exercise Completion Tracking (NEW FEATURE)
        if created_split:
            completion_success = self.test_completion_tracking_flow(created_split['id'])
            if not completion_success:
                print("⚠️  Completion tracking tests failed")
        
        # Test 7: Cleanup - Delete created split
        if created_split:
            self.test_delete_workout_split(created_split['id'])
        
        # Print summary
        self.print_summary()
        return True
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("🏋️ WORKOUT TRACKER API TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if total - passed > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['message']}")
        
        print("\n✅ All tests completed!")

if __name__ == "__main__":
    tester = WorkoutAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)