import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import styles from './AuthModal.module.css';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  mode: 'signin' | 'signup';
  onSwitchMode: () => void;
}

const AuthModal: React.FC<AuthModalProps> = ({ isOpen, onClose, mode, onSwitchMode }) => {
  const { login, signup } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form state
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [technicalLevel, setTechnicalLevel] = useState('beginner');
  const [programmingExp, setProgrammingExp] = useState<string[]>([]);
  const [roboticsBackground, setRoboticsBackground] = useState('none');
  const [learningGoals, setLearningGoals] = useState('');

  if (!isOpen) return null;

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      await login(email, password);
      onClose();
      resetForm();
    } catch (err: any) {
      setError(err.message || 'Login failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSignUp = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      await signup({
        email,
        password,
        name,
        technical_level: technicalLevel,
        programming_experience: programmingExp,
        robotics_background: roboticsBackground,
        learning_goals: learningGoals
      });
      onClose();
      resetForm();
    } catch (err: any) {
      setError(err.message || 'Signup failed');
    } finally {
      setIsLoading(false);
    }
  };

  const resetForm = () => {
    setEmail('');
    setPassword('');
    setName('');
    setTechnicalLevel('beginner');
    setProgrammingExp([]);
    setRoboticsBackground('none');
    setLearningGoals('');
    setError(null);
  };

  const toggleProgrammingExp = (lang: string) => {
    if (programmingExp.includes(lang)) {
      setProgrammingExp(programmingExp.filter(l => l !== lang));
    } else {
      setProgrammingExp([...programmingExp, lang]);
    }
  };

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <button className={styles.closeButton} onClick={onClose}>✕</button>

        <h2>{mode === 'signin' ? 'Sign In' : 'Create Account'}</h2>

        {error && <div className={styles.error}>{error}</div>}

        <form onSubmit={mode === 'signin' ? handleSignIn : handleSignUp}>
          {mode === 'signup' && (
            <div className={styles.formGroup}>
              <label>Name (Optional)</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Your name"
              />
            </div>
          )}

          <div className={styles.formGroup}>
            <label>Email *</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="you@example.com"
            />
          </div>

          <div className={styles.formGroup}>
            <label>Password *</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="Minimum 8 characters"
              minLength={8}
            />
          </div>

          {mode === 'signup' && (
            <>
              <div className={styles.formGroup}>
                <label>Technical Level *</label>
                <select value={technicalLevel} onChange={(e) => setTechnicalLevel(e.target.value)}>
                  <option value="beginner">Beginner - New to programming/robotics</option>
                  <option value="intermediate">Intermediate - Some programming experience</option>
                  <option value="advanced">Advanced - Professional/Research level</option>
                </select>
              </div>

              <div className={styles.formGroup}>
                <label>Programming Experience</label>
                <div className={styles.checkboxGroup}>
                  {['python', 'javascript', 'cpp', 'ros', 'other'].map(lang => (
                    <label key={lang} className={styles.checkbox}>
                      <input
                        type="checkbox"
                        checked={programmingExp.includes(lang)}
                        onChange={() => toggleProgrammingExp(lang)}
                      />
                      {lang === 'cpp' ? 'C++' : lang === 'ros' ? 'ROS' : lang.charAt(0).toUpperCase() + lang.slice(1)}
                    </label>
                  ))}
                </div>
              </div>

              <div className={styles.formGroup}>
                <label>Robotics Background *</label>
                <select value={roboticsBackground} onChange={(e) => setRoboticsBackground(e.target.value)}>
                  <option value="none">None - Complete beginner</option>
                  <option value="hobbyist">Hobbyist - Personal projects</option>
                  <option value="professional">Professional - Industry experience</option>
                  <option value="researcher">Researcher - Academic background</option>
                </select>
              </div>

              <div className={styles.formGroup}>
                <label>Learning Goals (Optional)</label>
                <textarea
                  value={learningGoals}
                  onChange={(e) => setLearningGoals(e.target.value)}
                  placeholder="What do you want to learn from this textbook?"
                  rows={3}
                />
              </div>
            </>
          )}

          <button
            type="submit"
            className={styles.submitButton}
            disabled={isLoading}
          >
            {isLoading ? 'Please wait...' : mode === 'signin' ? 'Sign In' : 'Create Account'}
          </button>
        </form>

        <div className={styles.switchMode}>
          {mode === 'signin' ? (
            <p>
              Don't have an account?{' '}
              <button onClick={onSwitchMode}>Sign Up</button>
            </p>
          ) : (
            <p>
              Already have an account?{' '}
              <button onClick={onSwitchMode}>Sign In</button>
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default AuthModal;
