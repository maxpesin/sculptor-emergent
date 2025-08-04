import React, { useState, useEffect } from 'react';
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Main App Component
function App() {
  const [currentView, setCurrentView] = useState('home');
  const [workoutSplits, setWorkoutSplits] = useState([]);
  const [currentSplit, setCurrentSplit] = useState(null);
  const [exercises, setExercises] = useState([]);
  const [muscleGroups, setMuscleGroups] = useState([]);

  useEffect(() => {
    fetchMuscleGroups();
    fetchWorkoutSplits();
    fetchExercises();
  }, []);

  const fetchMuscleGroups = async () => {
    try {
      const response = await axios.get(`${API}/muscle-groups`);
      setMuscleGroups(response.data);
    } catch (error) {
      console.error('Error fetching muscle groups:', error);
    }
  };

  const fetchWorkoutSplits = async () => {
    try {
      const response = await axios.get(`${API}/splits`);
      setWorkoutSplits(response.data);
    } catch (error) {
      console.error('Error fetching workout splits:', error);
    }
  };

  const fetchExercises = async () => {
    try {
      const response = await axios.get(`${API}/exercises`);
      setExercises(response.data);
    } catch (error) {
      console.error('Error fetching exercises:', error);
    }
  };

  const renderView = () => {
    switch (currentView) {
      case 'home':
        return <HomeView setCurrentView={setCurrentView} workoutSplits={workoutSplits} setCurrentSplit={setCurrentSplit} />;
      case 'create-split':
        return <CreateSplitView setCurrentView={setCurrentView} muscleGroups={muscleGroups} fetchWorkoutSplits={fetchWorkoutSplits} />;
      case 'workout':
        return <WorkoutView currentSplit={currentSplit} exercises={exercises} setCurrentView={setCurrentView} />;
      case 'exercise-archive':
        return <ExerciseArchiveView exercises={exercises} muscleGroups={muscleGroups} setCurrentView={setCurrentView} />;
      default:
        return <HomeView setCurrentView={setCurrentView} workoutSplits={workoutSplits} setCurrentSplit={setCurrentSplit} />;
    }
  };

  return (
    <div className="App">
      <Navigation currentView={currentView} setCurrentView={setCurrentView} />
      {renderView()}
    </div>
  );
}

// Navigation Component
const Navigation = ({ currentView, setCurrentView }) => {
  return (
    <nav className="nav-header">
      <div className="nav-brand">
        <h1 className="brand-display">💀 UndergroundGym</h1>
      </div>
      <div className="nav-links">
        <button 
          className={`nav-link ${currentView === 'home' ? 'active' : ''}`}
          onClick={() => setCurrentView('home')}
        >
          🏠 Home
        </button>
        <button 
          className={`nav-link ${currentView === 'create-split' ? 'active' : ''}`}
          onClick={() => setCurrentView('create-split')}
        >
          ⚡ Create Split
        </button>
        <button 
          className={`nav-link ${currentView === 'exercise-archive' ? 'active' : ''}`}
          onClick={() => setCurrentView('exercise-archive')}
        >
          📋 Exercise Archive
        </button>
      </div>
    </nav>
  );
};

// Home View Component
const HomeView = ({ setCurrentView, workoutSplits, setCurrentSplit }) => {
  const handleStartWorkout = (split, dayNumber) => {
    setCurrentSplit({ ...split, currentDay: dayNumber });
    setCurrentView('workout');
  };

  return (
    <div className="home-view">
      <section className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">💪 UNDERGROUND TRAINING</h1>
          <p className="hero-subtitle">
            No bullsh*t. No excuses. Just pure iron and gains in the darkness.
          </p>
          <div className="hero-actions">
            <button 
              className="btn-primary"
              onClick={() => setCurrentView('create-split')}
            >
              🔥 Create New Split
            </button>
            <button 
              className="btn-secondary"
              onClick={() => setCurrentView('exercise-archive')}
            >
              📚 Browse Arsenal
            </button>
          </div>
        </div>
      </section>

      <section className="splits-section">
        <div className="container">
          <h2 className="heading-2">⚔️ Your Training Splits</h2>
          {workoutSplits.length > 0 ? (
            <div className="company-grid">
              {workoutSplits.map(split => (
                <div key={split.id} className="service-card">
                  <div className="service-card-title">💀 {split.name}</div>
                  <div className="service-card-description">
                    🗓️ {split.days_per_week} days per week
                  </div>
                  <div className="split-days">
                    {split.days.map(day => (
                      <button
                        key={day.day_number}
                        className="btn-secondary day-button"
                        onClick={() => handleStartWorkout(split, day.day_number)}
                      >
                        💥 Day {day.day_number}: {day.day_name}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <p className="body-large">🎯 No training splits created yet</p>
              <p className="body-medium">Time to build your underground arsenal</p>
              <button 
                className="btn-primary"
                onClick={() => setCurrentView('create-split')}
              >
                🔥 Create Your First Split
              </button>
            </div>
          )}
        </div>
      </section>
    </div>
  );
};

// Create Split View Component
const CreateSplitView = ({ setCurrentView, muscleGroups, fetchWorkoutSplits }) => {
  const [splitName, setSplitName] = useState('');
  const [daysPerWeek, setDaysPerWeek] = useState(3);
  const [days, setDays] = useState([]);
  const [templates, setTemplates] = useState({});

  useEffect(() => {
    fetchTemplates();
    initializeDays(daysPerWeek);
  }, [daysPerWeek]);

  const fetchTemplates = async () => {
    try {
      const response = await axios.get(`${API}/templates`);
      setTemplates(response.data);
    } catch (error) {
      console.error('Error fetching templates:', error);
    }
  };

  const initializeDays = (numDays) => {
    const newDays = Array.from({ length: numDays }, (_, index) => ({
      day_number: index + 1,
      day_name: `Day ${index + 1}`,
      muscle_groups: [],
      exercises: []
    }));
    setDays(newDays);
  };

  const updateDay = (dayIndex, field, value) => {
    const updatedDays = [...days];
    updatedDays[dayIndex] = { ...updatedDays[dayIndex], [field]: value };
    setDays(updatedDays);
  };

  const toggleMuscleGroup = (dayIndex, muscleGroup) => {
    const updatedDays = [...days];
    const currentGroups = updatedDays[dayIndex].muscle_groups;
    
    if (currentGroups.includes(muscleGroup)) {
      updatedDays[dayIndex].muscle_groups = currentGroups.filter(mg => mg !== muscleGroup);
    } else {
      updatedDays[dayIndex].muscle_groups = [...currentGroups, muscleGroup];
    }
    
    setDays(updatedDays);
  };

  const useTemplate = (templateKey) => {
    const template = templates[templateKey];
    if (template) {
      setSplitName(template.name);
      setDaysPerWeek(template.days_per_week);
      setDays(template.days);
    }
  };

  const createSplit = async () => {
    if (!splitName.trim() || days.some(day => day.muscle_groups.length === 0)) {
      alert('Please fill in all required fields');
      return;
    }

    try {
      const splitData = {
        name: splitName,
        days_per_week: daysPerWeek,
        days: days
      };

      await axios.post(`${API}/splits`, splitData);
      await fetchWorkoutSplits();
      setCurrentView('home');
    } catch (error) {
      console.error('Error creating split:', error);
      alert('Error creating workout split');
    }
  };

  return (
    <div className="create-split-view">
      <div className="container">
        <h1 className="heading-1">Create Workout Split</h1>
        
        <div className="templates-section">
          <h3 className="heading-3">Quick Templates</h3>
          <div className="template-buttons">
            {Object.entries(templates).map(([key, template]) => (
              <button
                key={key}
                className="btn-secondary"
                onClick={() => useTemplate(key)}
              >
                {template.name}
              </button>
            ))}
          </div>
        </div>

        <div className="split-form">
          <div className="form-group">
            <label className="form-label">Split Name</label>
            <input
              type="text"
              className="form-input"
              value={splitName}
              onChange={(e) => setSplitName(e.target.value)}
              placeholder="My Custom Split"
            />
          </div>

          <div className="form-group">
            <label className="form-label">Days Per Week</label>
            <select 
              className="form-select"
              value={daysPerWeek}
              onChange={(e) => setDaysPerWeek(parseInt(e.target.value))}
            >
              <option value={3}>3 Days</option>
              <option value={4}>4 Days</option>
              <option value={5}>5 Days</option>
              <option value={6}>6 Days</option>
            </select>
          </div>

          <div className="days-section">
            <h3 className="heading-3">Configure Days</h3>
            {days.map((day, dayIndex) => (
              <div key={dayIndex} className="day-config">
                <div className="day-header">
                  <h4 className="heading-4">Day {day.day_number}</h4>
                  <input
                    type="text"
                    className="day-name-input"
                    value={day.day_name}
                    onChange={(e) => updateDay(dayIndex, 'day_name', e.target.value)}
                    placeholder="Day name"
                  />
                </div>
                
                <div className="muscle-groups-selection">
                  <p className="body-medium">Select muscle groups for this day:</p>
                  <div className="muscle-group-chips">
                    {muscleGroups.map(muscleGroup => (
                      <button
                        key={muscleGroup}
                        className={`muscle-chip ${day.muscle_groups.includes(muscleGroup) ? 'selected' : ''}`}
                        onClick={() => toggleMuscleGroup(dayIndex, muscleGroup)}
                      >
                        {muscleGroup}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="form-actions">
            <button className="btn-secondary" onClick={() => setCurrentView('home')}>
              Cancel
            </button>
            <button className="btn-primary" onClick={createSplit}>
              Create Split
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Workout View Component
const WorkoutView = ({ currentSplit, exercises, setCurrentView }) => {
  const [workoutExercises, setWorkoutExercises] = useState([]);
  const [currentDay, setCurrentDay] = useState(null);
  const [currentSessionId, setCurrentSessionId] = useState(null);

  // Rep options dropdown
  const repOptions = [
    { value: 8, label: '8 reps' },
    { value: 10, label: '10 reps' },
    { value: 12, label: '12 reps' },
    { value: 14, label: '14 reps' },
    { value: 15, label: '15 reps' },
    { value: 20, label: '20 reps' }
  ];

  useEffect(() => {
    if (currentSplit) {
      const day = currentSplit.days.find(d => d.day_number === currentSplit.currentDay);
      setCurrentDay(day);
      
      if (day) {
        const dayExercises = [];
        day.muscle_groups.forEach(muscleGroup => {
          const muscleExercises = exercises
            .filter(ex => ex.muscle_group === muscleGroup)
            .slice(0, 3);
          
          muscleExercises.forEach(exercise => {
            dayExercises.push({
              exercise_id: exercise.id,
              exercise_name: exercise.name,
              muscle_group: exercise.muscle_group,
              sets: [
                { set_number: 1, weight: 0, reps: 12 },
                { set_number: 2, weight: 0, reps: 12 },
                { set_number: 3, weight: 0, reps: 12 }
              ],
              completed_count: 0,
              target_completions: 3,
              is_archived: false
            });
          });
        });
        setWorkoutExercises(dayExercises);
      }
    }
  }, [currentSplit, exercises]);

  const updateSet = (exerciseIndex, setIndex, field, value) => {
    const updated = [...workoutExercises];
    if (field === 'reps') {
      updated[exerciseIndex].sets[setIndex][field] = parseInt(value) || 12;
    } else {
      updated[exerciseIndex].sets[setIndex][field] = parseFloat(value) || 0;
    }
    setWorkoutExercises(updated);
  };

  const completeExercise = async (exerciseIndex) => {
    if (!currentSessionId) {
      // Create session first if it doesn't exist
      await saveWorkout(true);
      return;
    }

    try {
      const exercise = workoutExercises[exerciseIndex];
      const response = await axios.patch(`${API}/sessions/${currentSessionId}/exercises/${exercise.exercise_id}/complete`);
      
      // Update local state
      const updated = [...workoutExercises];
      updated[exerciseIndex].completed_count = response.data.completed_count;
      updated[exerciseIndex].is_archived = response.data.is_archived;
      setWorkoutExercises(updated);

      // Show completion message
      if (response.data.is_archived) {
        alert(`🔥 BEAST MODE! "${exercise.exercise_name}" conquered and archived! 💀`);
      } else {
        alert(`💪 REP COMPLETED! ${response.data.completed_count}/${exercise.target_completions} reps done. Keep grinding! ⚡`);
      }
    } catch (error) {
      console.error('Error completing exercise:', error);
      alert('❌ Error completing exercise');
    }
  };

  const resetExerciseCompletion = async (exerciseIndex) => {
    if (!currentSessionId) return;

    try {
      const exercise = workoutExercises[exerciseIndex];
      const response = await axios.patch(`${API}/sessions/${currentSessionId}/exercises/${exercise.exercise_id}/reset`);
      
      // Update local state
      const updated = [...workoutExercises];
      updated[exerciseIndex].completed_count = 0;
      updated[exerciseIndex].is_archived = false;
      setWorkoutExercises(updated);

      alert('🔄 Exercise reset - Back to the grind!');
    } catch (error) {
      console.error('Error resetting exercise:', error);
      alert('❌ Error resetting exercise completion');
    }
  };

  const saveWorkout = async (createSessionOnly = false) => {
    try {
      const sessionData = {
        split_id: currentSplit.id,
        day_number: currentSplit.currentDay,
        exercises: workoutExercises
      };

      const response = await axios.post(`${API}/sessions`, sessionData);
      setCurrentSessionId(response.data.id);

      if (!createSessionOnly) {
        alert('💀 Workout logged in the underground archives!');
        setCurrentView('home');
      }
    } catch (error) {
      console.error('Error saving workout:', error);
      alert('❌ Error saving workout');
    }
  };

  if (!currentDay) {
    return <div className="loading">🔄 Loading your arsenal...</div>;
  }

  // Separate active and archived exercises
  const activeExercises = workoutExercises.filter(ex => !ex.is_archived);
  const archivedExercises = workoutExercises.filter(ex => ex.is_archived);

  const renderCompactExercises = (exercisesToRender, isArchived = false) => {
    const groupedExercises = exercisesToRender.reduce((acc, exercise) => {
      if (!acc[exercise.muscle_group]) {
        acc[exercise.muscle_group] = [];
      }
      acc[exercise.muscle_group].push(exercise);
      return acc;
    }, {});

    return Object.entries(groupedExercises).map(([muscleGroup, groupExercises]) => (
      <div key={`${muscleGroup}-${isArchived ? 'archived' : 'active'}`} className="muscle-group-section">
        <h2 className="heading-2">
          {getMuscleEmoji(muscleGroup)} {muscleGroup} {isArchived && '(💀 Conquered)'}
        </h2>
        
        <div className="compact-exercises-grid">
          {groupExercises.map((exercise, exerciseIndex) => {
            const globalIndex = workoutExercises.findIndex(we => 
              we.exercise_id === exercise.exercise_id && 
              we.muscle_group === exercise.muscle_group
            );
            
            return (
              <div key={`${exercise.exercise_id}-${muscleGroup}`} className={`compact-exercise-card ${isArchived ? 'archived' : ''}`}>
                <div className="exercise-header">
                  <h3 className="exercise-name">{exercise.exercise_name}</h3>
                  <div className="exercise-completion">
                    <span className="completion-count">
                      {exercise.completed_count}/{exercise.target_completions}
                    </span>
                    {!isArchived && (
                      <button
                        className="btn-complete"
                        onClick={() => completeExercise(globalIndex)}
                      >
                        ✅ Complete
                      </button>
                    )}
                    {isArchived && (
                      <button
                        className="btn-reset"
                        onClick={() => resetExerciseCompletion(globalIndex)}
                      >
                        🔄 Reset
                      </button>
                    )}
                  </div>
                </div>
                
                <div className="compact-sets-grid">
                  {exercise.sets.map((set, setIndex) => (
                    <div key={setIndex} className="compact-set-row">
                      <span className="set-number">Set {set.set_number}</span>
                      <div className="set-inputs">
                        <input
                          type="number"
                          className="weight-input"
                          value={set.weight}
                          onChange={(e) => updateSet(globalIndex, setIndex, 'weight', e.target.value)}
                          placeholder="Weight"
                          disabled={isArchived}
                        />
                        <select
                          className="reps-select"
                          value={set.reps}
                          onChange={(e) => updateSet(globalIndex, setIndex, 'reps', e.target.value)}
                          disabled={isArchived}
                        >
                          {repOptions.map(option => (
                            <option key={option.value} value={option.value}>
                              {option.label}
                            </option>
                          ))}
                        </select>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    ));
  };

  const getMuscleEmoji = (muscleGroup) => {
    const emojiMap = {
      'Chest': '💥',
      'Back': '🦵',
      'Shoulders': '🔥',
      'Arms': '💪',
      'Legs': '🦵',
      'Core': '⚡'
    };
    return emojiMap[muscleGroup] || '💀';
  };

  return (
    <div className="workout-view">
      <div className="container">
        <div className="workout-header">
          <h1 className="heading-1">💀 {currentDay.day_name}</h1>
          <p className="body-large">🎯 Target: {currentDay.muscle_groups.join(', ')}</p>
        </div>

        <div className="workout-content">
          {/* Active Exercises */}
          {activeExercises.length > 0 && (
            <div className="active-exercises">
              <h2 className="section-title">⚔️ ACTIVE ARSENAL</h2>
              {renderCompactExercises(activeExercises, false)}
            </div>
          )}
          
          {/* Archived Exercises */}
          {archivedExercises.length > 0 && (
            <div className="archived-exercises">
              <h2 className="section-title">💀 CONQUERED EXERCISES</h2>
              {renderCompactExercises(archivedExercises, true)}
            </div>
          )}
        </div>

        <div className="workout-actions">
          <button className="btn-secondary" onClick={() => setCurrentView('home')}>
            🏠 Back to Base
          </button>
          <button className="btn-primary" onClick={() => saveWorkout(false)}>
            💾 Log Session
          </button>
        </div>
      </div>
    </div>
  );
};

// Exercise Archive View Component
const ExerciseArchiveView = ({ exercises, muscleGroups, setCurrentView }) => {
  const [selectedMuscleGroup, setSelectedMuscleGroup] = useState('');
  const [searchTerm, setSearchTerm] = useState('');

  const filteredExercises = exercises.filter(exercise => {
    const matchesMuscleGroup = !selectedMuscleGroup || exercise.muscle_group === selectedMuscleGroup;
    const matchesSearch = !searchTerm || 
      exercise.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      exercise.muscle_group.toLowerCase().includes(searchTerm.toLowerCase());
    
    return matchesMuscleGroup && matchesSearch;
  });

  return (
    <div className="exercise-archive-view">
      <div className="container">
        <h1 className="heading-1">Exercise Archive</h1>
        
        <div className="archive-filters">
          <div className="filter-group">
            <input
              type="text"
              className="search-input"
              placeholder="Search exercises..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            
            <select
              className="filter-select"
              value={selectedMuscleGroup}
              onChange={(e) => setSelectedMuscleGroup(e.target.value)}
            >
              <option value="">All Muscle Groups</option>
              {muscleGroups.map(group => (
                <option key={group} value={group}>{group}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="exercises-grid">
          {filteredExercises.map(exercise => (
            <div key={exercise.id} className="exercise-card">
              <div className="exercise-info">
                <h3 className="exercise-name">{exercise.name}</h3>
                <span className="exercise-muscle-group">{exercise.muscle_group}</span>
                {exercise.equipment && (
                  <span className="exercise-equipment">{exercise.equipment}</span>
                )}
              </div>
            </div>
          ))}
        </div>

        <div className="archive-actions">
          <button className="btn-secondary" onClick={() => setCurrentView('home')}>
            Back to Home
          </button>
        </div>
      </div>
    </div>
  );
};

export default App;