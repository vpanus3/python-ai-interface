import React from 'react';
import { createRoot } from 'react-dom/client';
import 'bootstrap/dist/css/bootstrap.min.css'; // Import Bootstrap CSS

import App from "./app";

const container = document.getElementById('root');
const root = createRoot(container);
root.render(<App tab="home" />);
