import React, { useRef, useEffect } from 'react';

export default function TypewriterText({ text, delay = 100, infinite = false }) {
    const spanRef = useRef(null);
    const requestRef = useRef();
    const startTimeRef = useRef();
    const indexRef = useRef(0);

    useEffect(() => {
        const node = spanRef.current;
        if (!node) return;

        // Reset
        indexRef.current = 0;
        node.innerText = ''; // Start empty
        // Use a cursor if you want, but text slice is simpler

        startTimeRef.current = null;

        const animate = (time) => {
            if (!startTimeRef.current) startTimeRef.current = time;
            const elapsed = time - startTimeRef.current;
            const targetIndex = Math.floor(elapsed / delay);

            if (targetIndex !== indexRef.current) {
                indexRef.current = targetIndex;
                if (indexRef.current <= text.length) {
                    node.innerText = text.slice(0, indexRef.current);
                }
            }

            if (indexRef.current < text.length) {
                requestRef.current = requestAnimationFrame(animate);
            } else if (infinite) {
                setTimeout(() => {
                    startTimeRef.current = null;
                    indexRef.current = 0;
                    node.innerText = '';
                    requestRef.current = requestAnimationFrame(animate);
                }, 2000);
            }
        };

        requestRef.current = requestAnimationFrame(animate);

        return () => cancelAnimationFrame(requestRef.current);
    }, [text, delay, infinite]);

    return <span ref={spanRef}></span>;
}
