import React, { useState, useEffect } from 'react';
import "./App.css";
import axios from "axios";
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd';

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
        <h1 className="brand-display">💪 Sculptor</h1>
      </div>
      <div className="nav-links">
        <button 
          className={`nav-link ${currentView === 'home' ? 'active' : ''}`}
          onClick={() => setCurrentView('home')}
        >
          🏛️ Colosseum
        </button>
        <button 
          className={`nav-link ${currentView === 'create-split' ? 'active' : ''}`}
          onClick={() => setCurrentView('create-split')}
        >
          ⚔️ Create Training
        </button>
        <button 
          className={`nav-link ${currentView === 'exercise-archive' ? 'active' : ''}`}
          onClick={() => setCurrentView('exercise-archive')}
        >
          📜 Exercise Codex
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

  // Show hero if no splits, show ONLY splits if they exist
  const showHeroOnly = workoutSplits.length === 0;

  if (showHeroOnly) {
    return (
      <div className="home-view">
        <section className="hero-section">
          <div className="hero-content">
            <h1 className="hero-title">⚔️ FORGE YOUR LEGEND</h1>
            <p className="hero-subtitle">
              "Discipline is the soul of an army. Train like a gladiator, fight like a champion."
            </p>
            <div className="hero-actions">
              <button 
                className="btn-primary"
                onClick={() => setCurrentView('create-split')}
              >
                🏛️ Create Training Regimen
              </button>
              <button 
                className="btn-secondary"
                onClick={() => setCurrentView('exercise-archive')}
              >
                📜 Study the Codex
              </button>
            </div>
          </div>
        </section>
      </div>
    );
  }

  // Show ONLY splits when they exist (no hero)
  return (
    <div className="home-view">
      <section className="splits-section">
        <div className="container">
          <div className="splits-header">
            <h1 className="splits-title">🏛️ Your Training Regimens</h1>
            <div className="splits-actions">
              <button 
                className="btn-primary"
                onClick={() => setCurrentView('create-split')}
              >
                ⚔️ Create New Regimen
              </button>
              <button 
                className="btn-secondary"
                onClick={() => setCurrentView('exercise-archive')}
              >
                📜 Browse Codex
              </button>
            </div>
          </div>
          
          <div className="gladiator-splits-grid">
            {workoutSplits.map(split => (
              <div key={split.id} className="gladiator-split-card">
                <div className="split-header">
                  <div className="split-title">⚔️ {split.name}</div>
                  <div className="split-description">
                    🗓️ {split.days_per_week} days per week
                  </div>
                </div>
                <div className="split-days-grid">
                  {split.days.map(day => (
                    <button
                      key={day.day_number}
                      className="gladiator-day-button"
                      onClick={() => handleStartWorkout(split, day.day_number)}
                    >
                      <div className="day-number">Day {day.day_number}</div>
                      <div className="day-name">{day.day_name}</div>
                      <div className="day-muscles">{day.muscle_groups.join(' • ')}</div>
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
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

  // Rep range options for each exercise
  const repRangeOptions = [
    { value: '6-10', label: '6-10 reps', min: 6, max: 10, default: 8 },
    { value: '8-12', label: '8-12 reps', min: 8, max: 12, default: 10 },
    { value: '10-14', label: '10-14 reps', min: 10, max: 14, default: 12 }
  ];

  // Weight options for dropdown
  const weightOptions = [
    0, 1, 2, 3, 4, 5, 7.5, 10, 12.5, 15, 17.5, 20, 22.5, 25, 27.5, 30, 
    32.5, 35, 37.5, 40, 42.5, 45, 47.5, 50, 55, 60, 65, 70, 75, 80, 85, 
    90, 95, 100, 105, 110, 115, 120, 125, 130, 135, 140, 145, 150, 160, 
    170, 180, 190, 200, 225, 250, 275, 300, 325, 350, 375, 400
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
              rep_range: '8-12', // Default rep range
              sets: [
                { set_number: 1, weight: 0 },
                { set_number: 2, weight: 0 },
                { set_number: 3, weight: 0 },
                { set_number: 4, weight: 0 }
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
    updated[exerciseIndex].sets[setIndex][field] = parseFloat(value) || 0;
    setWorkoutExercises(updated);
  };

  const updateExerciseRepRange = (exerciseIndex, repRange) => {
    const updated = [...workoutExercises];
    updated[exerciseIndex].rep_range = repRange;
    setWorkoutExercises(updated);
  };

  const completeExercise = async (exerciseIndex) => {
    if (!currentSessionId) {
      await saveWorkout(true);
      return;
    }

    try {
      const exercise = workoutExercises[exerciseIndex];
      const response = await axios.patch(`${API}/sessions/${currentSessionId}/exercises/${exercise.exercise_id}/complete`);
      
      const updated = [...workoutExercises];
      updated[exerciseIndex].completed_count = response.data.completed_count;
      updated[exerciseIndex].is_archived = response.data.is_archived;
      setWorkoutExercises(updated);

      if (response.data.is_archived) {
        alert(`⚔️ VICTORY! "${exercise.exercise_name}" has been conquered and archived! 🏛️`);
      } else {
        alert(`💪 PROGRESS! ${response.data.completed_count}/${exercise.target_completions} conquests. Continue your training! ⚔️`);
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
      
      const updated = [...workoutExercises];
      updated[exerciseIndex].completed_count = 0;
      updated[exerciseIndex].is_archived = false;
      setWorkoutExercises(updated);

      alert('🔄 Exercise reset - Return to the arena!');
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
        exercises: workoutExercises.map(ex => ({
          ...ex,
          sets: ex.sets.map(set => ({
            ...set,
            reps: repRangeOptions.find(r => r.value === ex.rep_range)?.default || 10
          }))
        }))
      };

      const response = await axios.post(`${API}/sessions`, sessionData);
      setCurrentSessionId(response.data.id);

      if (!createSessionOnly) {
        alert('⚔️ Your training has been recorded in the gladiator chronicles!');
        setCurrentView('home');
      }
    } catch (error) {
      console.error('Error saving workout:', error);
      alert('❌ Error saving workout');
    }
  };

  if (!currentDay) {
    return <div className="loading">🔄 Preparing the arena...</div>;
  }

  const activeExercises = workoutExercises.filter(ex => !ex.is_archived);
  const archivedExercises = workoutExercises.filter(ex => ex.is_archived);

  const renderGladiatorExercises = (exercisesToRender, isArchived = false) => {
    const groupedExercises = exercisesToRender.reduce((acc, exercise) => {
      if (!acc[exercise.muscle_group]) {
        acc[exercise.muscle_group] = [];
      }
      acc[exercise.muscle_group].push(exercise);
      return acc;
    }, {});

    return Object.entries(groupedExercises).map(([muscleGroup, groupExercises]) => (
      <div key={`${muscleGroup}-${isArchived ? 'archived' : 'active'}`} className="gladiator-muscle-section">
        <h2 className="muscle-section-title">
          {getMuscleEmoji(muscleGroup)} {muscleGroup} {isArchived && '(🏆 Conquered)'}
        </h2>
        
        <div className="stacked-exercises-container">
          {groupExercises.map((exercise, exerciseIndex) => {
            const globalIndex = workoutExercises.findIndex(we => 
              we.exercise_id === exercise.exercise_id && 
              we.muscle_group === exercise.muscle_group
            );
            
            return (
              <div key={`${exercise.exercise_id}-${muscleGroup}`} className={`stacked-exercise-card ${isArchived ? 'conquered' : ''}`}>
                <div className="exercise-header">
                  <div className="exercise-info">
                    <h3 className="exercise-name">{exercise.exercise_name}</h3>
                    <select
                      className="rep-range-select"
                      value={exercise.rep_range}
                      onChange={(e) => updateExerciseRepRange(globalIndex, e.target.value)}
                      disabled={isArchived}
                    >
                      {repRangeOptions.map(option => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="completion-tracker">
                    <span className="completion-count">
                      {exercise.completed_count}/{exercise.target_completions}
                    </span>
                    {!isArchived && (
                      <button
                        className="btn-complete"
                        onClick={() => completeExercise(globalIndex)}
                      >
                        ⚔️ Complete
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
                
                <div className="horizontal-sets-container">
                  {exercise.sets.map((set, setIndex) => (
                    <div key={setIndex} className="horizontal-set-card">
                      <div className="set-header">Set {set.set_number}</div>
                      <div className="set-weight-input">
                        <select
                          className="weight-select"
                          value={set.weight}
                          onChange={(e) => updateSet(globalIndex, setIndex, 'weight', e.target.value)}
                          disabled={isArchived}
                        >
                          {weightOptions.map(weight => (
                            <option key={weight} value={weight}>
                              {weight === 0 ? '-- lbs' : `${weight} lbs`}
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
      'Chest': '🛡️',
      'Back': '⚔️',
      'Shoulders': '🏛️',
      'Arms': '💪',
      'Legs': '🦵',
      'Core': '⚡'
    };
    return emojiMap[muscleGroup] || '⚔️';
  };

  return (
    <div className="gladiator-workout-view">
      <div className="container">
        <div className="arena-header">
          <h1 className="arena-title">⚔️ {currentDay.day_name}</h1>
          <p className="arena-subtitle">🎯 Focus: {currentDay.muscle_groups.join(' • ')}</p>
        </div>

        <div className="arena-content">
          {activeExercises.length > 0 && (
            <div className="active-training">
              <h2 className="section-title">⚔️ ACTIVE TRAINING</h2>
              {renderGladiatorExercises(activeExercises, false)}
            </div>
          )}
          
          {archivedExercises.length > 0 && (
            <div className="conquered-training">
              <h2 className="section-title">🏆 CONQUERED EXERCISES</h2>
              {renderGladiatorExercises(archivedExercises, true)}
            </div>
          )}
        </div>

        <div className="arena-actions">
          <button className="btn-secondary" onClick={() => setCurrentView('home')}>
            🏛️ Return to Colosseum
          </button>
          <button className="btn-primary" onClick={() => saveWorkout(false)}>
            📜 Record Victory
          </button>
        </div>
      </div>
    </div>
  );
};

// Exercise Archive View Component
const ExerciseArchiveView = ({ exercises, muscleGroups, setCurrentView }) => {
  const [selectedMuscleGroup, setSelectedMuscleGroup] = useState(muscleGroups[0] || 'Chest');
  const [searchTerm, setSearchTerm] = useState('');
  const [exerciseOrder, setExerciseOrder] = useState([]);
  const [exerciseHistory, setExerciseHistory] = useState({});

  useEffect(() => {
    setExerciseOrder(exercises.map(ex => ex.id));
    fetchExerciseHistory();
  }, [exercises]);

  const fetchExerciseHistory = async () => {
    try {
      const response = await axios.get(`${API}/sessions`);
      const sessions = response.data;
      
      const history = {};
      sessions.forEach(session => {
        session.exercises.forEach(exercise => {
          if (!history[exercise.exercise_id] || new Date(session.completed_at) > new Date(history[exercise.exercise_id].date)) {
            history[exercise.exercise_id] = {
              date: session.completed_at,
              sets: exercise.sets,
              completed_count: exercise.completed_count
            };
          }
        });
      });
      
      setExerciseHistory(history);
    } catch (error) {
      console.error('Error fetching exercise history:', error);
    }
  };

  const handleDragEnd = (result) => {
    if (!result.destination) return;

    const items = Array.from(exerciseOrder);
    const [reorderedItem] = items.splice(result.source.index, 1);
    items.splice(result.destination.index, 0, reorderedItem);

    setExerciseOrder(items);
  };

  const filteredExercises = exercises
    .filter(exercise => {
      const matchesMuscleGroup = exercise.muscle_group === selectedMuscleGroup;
      const matchesSearch = !searchTerm || 
        exercise.name.toLowerCase().includes(searchTerm.toLowerCase());
      
      return matchesMuscleGroup && matchesSearch;
    })
    .sort((a, b) => exerciseOrder.indexOf(a.id) - exerciseOrder.indexOf(b.id));

  const getMuscleEmoji = (muscleGroup) => {
    const emojiMap = {
      'Chest': '🛡️',
      'Back': '⚔️',
      'Shoulders': '🏛️',
      'Arms': '💪',
      'Legs': '🦵',
      'Core': '⚡'
    };
    return emojiMap[muscleGroup] || '⚔️';
  };

  const getLastWorkoutDisplay = (exercise) => {
    const history = exerciseHistory[exercise.id];
    if (!history || !history.sets || history.sets.length === 0) {
      return <span className="no-history">🆕 No battles yet</span>;
    }

    const lastSet = history.sets[history.sets.length - 1];
    const date = new Date(history.date).toLocaleDateString();
    
    return (
      <div className="gladiator-history">
        <div className="history-date">📅 {date}</div>
        <div className="history-details">
          ⚖️ {lastSet.weight}lbs × {lastSet.reps} reps
        </div>
        <div className="history-completions">
          🏆 {history.completed_count} victories
        </div>
      </div>
    );
  };

  return (
    <div className="gladiator-codex-view">
      <div className="container">
        <h1 className="codex-title">📜 THE GLADIATOR'S CODEX</h1>
        <p className="codex-subtitle">⚔️ Drag to reorder your training arsenal</p>
        
        <div className="codex-filters">
          <input
            type="text"
            className="codex-search"
            placeholder="🔍 Search the codex..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        {/* Muscle Group Tabs */}
        <div className="muscle-tabs">
          {muscleGroups.map(group => (
            <button
              key={group}
              className={`muscle-tab ${selectedMuscleGroup === group ? 'active' : ''}`}
              onClick={() => setSelectedMuscleGroup(group)}
            >
              {getMuscleEmoji(group)} {group}
            </button>
          ))}
        </div>

        <DragDropContext onDragEnd={handleDragEnd}>
          <Droppable droppableId="exercises">
            {(provided) => (
              <div
                className="codex-table"
                {...provided.droppableProps}
                ref={provided.innerRef}
              >
                <div className="codex-header">
                  <span className="col-handle">⚔️</span>
                  <span className="col-exercise">🏛️ Exercise</span>
                  <span className="col-equipment">⚔️ Equipment</span>
                  <span className="col-history">📊 Last Battle</span>
                </div>
                
                {filteredExercises.map((exercise, index) => (
                  <Draggable key={exercise.id} draggableId={exercise.id} index={index}>
                    {(provided, snapshot) => (
                      <div
                        ref={provided.innerRef}
                        {...provided.draggableProps}
                        {...provided.dragHandleProps}
                        className={`codex-row ${snapshot.isDragging ? 'dragging' : ''}`}
                      >
                        <span className="col-handle">⋮⋮</span>
                        <span className="col-exercise">
                          <strong>{exercise.name}</strong>
                        </span>
                        <span className="col-equipment">
                          {exercise.equipment || '🤲 Bodyweight'}
                        </span>
                        <span className="col-history">
                          {getLastWorkoutDisplay(exercise)}
                        </span>
                      </div>
                    )}
                  </Draggable>
                ))}
                
                {provided.placeholder}
              </div>
            )}
          </Droppable>
        </DragDropContext>

        <div className="codex-actions">
          <button className="btn-secondary" onClick={() => setCurrentView('home')}>
            🏛️ Return to Colosseum
          </button>
          <button className="btn-primary" onClick={() => window.location.reload()}>
            🔄 Refresh Codex
          </button>
        </div>
      </div>
    </div>
  );
};

export default App;