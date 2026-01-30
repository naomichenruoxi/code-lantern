// Static mock data for demo mode matching exact backend response structure

export const DEMO_PROJECT_SUMMARY = {
    project_name: "react-demo-app",
    project_path: "/tmp/uploads/demo-project",
    project_source: "github",
    generated_at: new Date().toISOString().split('T')[0],
    project_stats: {
        file_stats: {
            total_files: 42,
            total_lines: 3450,
            total_size: "1.2 MB",
            avg_file_size: "25 KB"
        },
        function_stats: {
            total_functions: 128,
            total_classes: 15,
            total_function_calls: 340,
            average_complexity: 4.2,
            max_complexity: 18
        },
        complexity_metrics: {
            project_size: "Medium",
            maintainability_index: 85,
            code_health_score: 92,
            cyclomatic_complexity_density: 0.12
        },
        language_stats: {
            language_percentages: {
                "JavaScript": 65,
                "CSS": 25,
                "HTML": 10
            },
            file_counts: {
                "js": 28,
                "css": 8,
                "html": 6
            }
        }
    },
    ai_summary: {
        source: "Gemini 1.5 Pro",
        overview: "This is a robust React application demonstrating modern patterns. It uses a component-based architecture with clean separation of concerns. The codebase is well-structured and follows best practices for state management.",
        architecture_insights: "The project follows a standard React project structure with source code in `src`, components isolated in their own directories, and utility functions separated. It likely uses a flux-like state management pattern.",
        technology_assessment: "Core technologies include React for UI, CSS modules for styling, and likely Webpack/Vite for bundling. Dependencies suggest a standard single-page application (SPA) setup.",
        strengths: [
            "Modular component design",
            "High code maintainability score (85/100)",
            "Low average cyclomatic complexity"
        ],
        recommendations: [
            "Consider adding unit tests for utility functions",
            "Optimize CSS imports for performance",
            "Add accessibility (A11y) attributes to interactive elements"
        ]
    }
};

export const DEMO_ANALYSIS_DATA = {
    // REQUIRED by ArchitectureTab COMPONENTS
    architecture_map: {
        listOfFiles: [
            {
                filePath: "src/App.jsx",
                imports: ["react", "./components/Header", "./components/Footer", "./utils"],
                listOfFunctions: [
                    { functionName: "App", line: 10, args: [], complexity: 3, calls: ["Header", "MainContent", "Footer"] }
                ],
                classes: []
            },
            {
                filePath: "src/utils.js",
                imports: [],
                listOfFunctions: [
                    { functionName: "calculateTotal", line: 5, args: ["items"], complexity: 2, calls: [] },
                    { functionName: "formatDate", line: 15, args: ["date"], complexity: 1, calls: [] }
                ],
                classes: []
            },
            {
                filePath: "src/components/Header.jsx",
                imports: ["react", "./Button"],
                listOfFunctions: [
                    { functionName: "Header", line: 8, args: ["props"], complexity: 2, calls: ["Button"] }
                ],
                classes: []
            },
            {
                filePath: "src/components/Button.jsx",
                imports: ["react"],
                listOfFunctions: [
                    { functionName: "Button", line: 5, args: ["onClick", "label"], complexity: 1, calls: [] }
                ],
                classes: []
            },
            {
                filePath: "src/components/Footer.jsx",
                imports: ["react"],
                listOfFunctions: [
                    { functionName: "Footer", line: 5, args: [], complexity: 1, calls: [] }
                ],
                classes: []
            },
            {
                filePath: "src/components/MainContent.jsx",
                imports: ["react"],
                listOfFunctions: [
                    { functionName: "MainContent", line: 5, args: [], complexity: 1, calls: [] }
                ],
                classes: []
            }
        ]
    },

    // REQUIRED by OverviewTab -> directory_tree
    directory_tree: {
        name: "root",
        path: "/",
        type: "directory",
        children: [
            {
                name: "src",
                path: "/src",
                type: "directory",
                children: [
                    {
                        name: "components",
                        path: "/src/components",
                        type: "directory",
                        children: [
                            { name: "Header.jsx", path: "/src/components/Header.jsx", type: "file", complexity: 5 },
                            { name: "Button.jsx", path: "/src/components/Button.jsx", type: "file", complexity: 3 },
                            { name: "Footer.jsx", path: "/src/components/Footer.jsx", type: "file", complexity: 2 }
                        ]
                    },
                    { name: "App.jsx", path: "/src/App.jsx", type: "file", complexity: 12 },
                    { name: "index.js", path: "/src/index.js", type: "file", complexity: 4 },
                    { name: "utils.js", path: "/src/utils.js", type: "file", complexity: 8 }
                ]
            },
            {
                name: "public",
                path: "/public",
                type: "directory",
                children: [
                    { name: "index.html", path: "/public/index.html", type: "file", complexity: 1 }
                ]
            },
            { name: "package.json", path: "/package.json", type: "file", complexity: 1 }
        ]
    },

    // REQUIRED by ComplexityHeatmap
    complexity_metrics: {
        "src/App.jsx": 15,
        "src/utils.js": 12,
        "src/components/Button.jsx": 5
    },

    // REQUIRED for Deep Dive Tab - Normalized to what API returns
    function_details_map: {
        "src/App.jsx::App": {
            inputs: "None",
            outputs: "JSX.Element",
            description: "Root component that sets up the main application layout structure involving Header, MainContent, and Footer.",
            calls: ["Header", "MainContent", "Footer"]
        },
        "src/utils.js::calculateTotal": {
            inputs: "items (Array), tax (Number)",
            outputs: "Number (Total Price)",
            description: "Utility function that aggregates the price of all items in the cart and applies the given tax rate to return final total.",
            calls: []
        },
        "src/utils.js::formatDate": {
            inputs: "date (Date|String)",
            outputs: "String (Formatted Date)",
            description: "Formats a date object into a readable 'YYYY-MM-DD' string format for UI display.",
            calls: []
        },
        "src/components/Header.jsx::Header": {
            inputs: "props",
            outputs: "JSX.Element",
            description: "Renders the top navigation bar and handles user session display.",
            calls: ["Button"]
        },
        "src/components/Button.jsx::Button": {
            inputs: "onClick (Function), label (String)",
            outputs: "JSX.Element",
            description: "Reusable button button component with hover states and click handling.",
            calls: []
        },
        "src/components/Footer.jsx::Footer": {
            inputs: "None",
            outputs: "JSX.Element",
            description: "Renders the site footer with copyright info.",
            calls: []
        }
    }
};
