import React, { useEffect } from 'react';
import { Provider } from 'react-redux';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { store } from './store/store';
import Login from './components/Login';
import Register from './components/Register';
import { useSelector } from 'react-redux';

const Navigation = () => {
  const { isAuthenticated } = useSelector((state) => state.auth);

  useEffect(() => {
    // Theme toggle functionality
    const toggleTheme = () => {
      document.body.classList.toggle('dark-mode');
      const logo = document.getElementById('logo');
      if (logo) {
        const isDarkMode = document.body.classList.contains('dark-mode');
        logo.src = isDarkMode ? logo.dataset.dark : logo.dataset.light;
      }
    };

    const themeButton = document.getElementById('toggle-theme');
    if (themeButton) {
      themeButton.addEventListener('click', toggleTheme);
    }

    return () => {
      if (themeButton) {
        themeButton.removeEventListener('click', toggleTheme);
      }
    };
  }, []);

  return (
    <div id="top-navbar">
      <div className="nav-container">
        <div className="logo">
          <Link to="/">
            <img 
              id="logo"
              src="/static/revizo/images/logo.png"
              data-light="/static/revizo/images/logo.png"
              data-dark="/static/revizo/images/darklogo.png"
              alt="Revizo Logo"
            />
          </Link>
        </div>
        <ul className="nav-links">
          <li><Link to="/flashcards">Manage Flashcards</Link></li>
        </ul>
        <div className="auth-links">
          {isAuthenticated ? (
            <Link to="/logout">Logout</Link>
          ) : (
            <>
              <Link to="/register">Sign Up</Link>
              <Link to="/login">Login</Link>
            </>
          )}
          <button id="toggle-theme" className="night-mode-toggle">🌙</button>
        </div>
      </div>
    </div>
  );
};

const App = () => {
  return (
    <Provider store={store}>
      <Router>
        <div className="app">
          <Navigation />
          <main id="main-content">
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              {/* Add more routes as needed */}
            </Routes>
          </main>
          <footer>
            <div className="footer-container">
              <p><Link to="/about">About</Link></p>
              <p><Link to="/contact">Contact Us</Link></p>
              <p>&copy; 2025 Revizo. All rights reserved.</p>
            </div>
          </footer>
        </div>
      </Router>
    </Provider>
  );
};

export default App; 