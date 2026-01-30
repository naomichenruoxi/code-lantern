/**
 * Converts architecture map to Cytoscape elements with compound nodes
 * Files are parent nodes, functions are child nodes
 */
export default function convertToGraph(architectureData) {
  const elements = [];
  const functionIds = new Set();

  // Color palette for files (darker, vibrant colors for dark background)
  const fileColors = [
    '#1a2332', '#2a1a23', '#1a2a23', '#2a2a1a',
    '#231a2a', '#1a232a', '#2a231a', '#1a1a2a'
  ];

  const funcColor = '#4FB3FF'; // Bright blue for functions

  if (!architectureData || !architectureData.listOfFiles) {
    return elements;
  }

  // Create file (parent) and function (child) nodes
  // Skip files with no functions to avoid empty circles
  architectureData.listOfFiles.forEach((file, fileIndex) => {
    const filePath = file.filePath;
    const fileId = `file-${fileIndex}`;
    const fileName = filePath.split('/').pop() || filePath;

    // Only add file if it has functions
    if (file.listOfFunctions && file.listOfFunctions.length > 0) {
      // Add file as parent node
      elements.push({
        data: {
          id: fileId,
          label: filePath,
          fileColor: fileColors[fileIndex % fileColors.length]
        }
      });

      // Add functions as child nodes
      file.listOfFunctions.forEach((func) => {
        const funcId = func.functionName;
        const funcLabel = funcId.split('-').pop() || funcId;

        functionIds.add(funcId);

        elements.push({
          data: {
            id: funcId,
            label: funcLabel,
            parent: fileId,
            funcColor: funcColor,
            complexity: func.complexity || 1,
            lines: func.lines || 0
          }
        });
      });

    }
  });

  // Create edges for function calls
  architectureData.listOfFiles.forEach((file) => {
    if (file.listOfFunctions) {
      file.listOfFunctions.forEach((func) => {
        const sourceId = func.functionName;

        if (func.calls && func.calls.length > 0) {
          func.calls.forEach((calledFunc) => {
            // Try to find matching target function
            // First try exact match, then try simple name match
            let targetId = null;

            if (functionIds.has(calledFunc)) {
              targetId = calledFunc;
            } else {
              // Try to find by simple name
              for (const funcId of functionIds) {
                const simpleName = funcId.split('-').pop();
                if (simpleName === calledFunc) {
                  targetId = funcId;
                  break;
                }
              }
            }

            if (targetId && functionIds.has(sourceId)) {
              elements.push({
                data: {
                  id: `${sourceId}->${targetId}`,
                  source: sourceId,
                  target: targetId
                }
              });
            }
          });
        }
      });
    }
  });

  return elements;
}
