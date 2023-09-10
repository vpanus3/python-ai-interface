import React from 'react';
import ReactDOM from 'react-dom';
import { createRoot } from 'react-dom/client';
import 'bootstrap/dist/css/bootstrap.min.css'; // Import Bootstrap CSS

const App = () => {
  return (
    <div className="container">
      {/* <h1>Hello World</h1> */}
    </div>
  );
};

const container = document.getElementById('app');
const root = createRoot(container);
root.render(<App tab="home" />);
