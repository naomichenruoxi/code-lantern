// import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
// import UploadPage from "./pages/UploadPage";
// import ProjectDetailPage from "./pages/ProjectDetailPage";

// export default function App() {
//   return (
//     <Router>
//       <Routes>
//         <Route path="/" element={<UploadPage />} />
//         <Route path="/project" element={<ProjectDetailPage />} />
//       </Routes>
//     </Router>
//   );
// }
// export default function App() {
//     return (
//       <div className="w-screen h-screen bg-gray-900 text-white flex items-center justify-center text-4xl">
//         Hello from App.jsx 👋
//       </div>
//     );
//   }

// import React from 'react';
// import FunctionCallGraph from './components/FunctionCallGraph';

// function App() {
//   return (
//     <div style={{ width: '100%', height: '100vh' }}>
//       <FunctionCallGraph />
//     </div>
//   );
// }

// export default App;

import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import UploadPage from "./pages/UploadPage";
import ProjectDetailPage from "./pages/ProjectDetailPage";

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<UploadPage />} />
        <Route path="/project/:repoId" element={<ProjectDetailPage />} />
      </Routes>
    </Router>
  );
}




// export default function App() {
//   return (
//     <Router>
//       <Routes>
//         <Route path="/" element={<UploadPage />} />
//         <Route path="/project" element={<ProjectDetailPage />} />
//       </Routes>
//     </Router>
//   );
// }

// export default function App() {
//     return (
//       <div className="flex items-center justify-center h-screen bg-gray-100">
//         <h1 className="text-4xl font-bold text-blue-600">
//           Tailwind is working! 🎉
//         </h1>
//       </div>
//     );
//   }

