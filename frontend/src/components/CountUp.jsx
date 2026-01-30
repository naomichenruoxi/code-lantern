import React, { useState, useEffect } from 'react';

export default function CountUp({ end, duration = 2000, suffix = '' }) {
    const spanRef = React.useRef(null);

    useEffect(() => {
        const node = spanRef.current;
        if (!node) return;

        let startTime;
        let animationFrame;

        // Parse numeric part
        const numericEnd = parseInt(end.toString().replace(/[^0-9]/g, ''), 10);
        if (isNaN(numericEnd)) {
            node.innerText = end;
            return;
        }

        const step = (timestamp) => {
            if (!startTime) startTime = timestamp;
            const progress = Math.min((timestamp - startTime) / duration, 1);

            // Easing function (easeOutExpo)
            const easeVal = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);

            const currentVal = Math.floor(numericEnd * easeVal);
            node.innerText = `${currentVal}${suffix}`;

            if (progress < 1) {
                animationFrame = requestAnimationFrame(step);
            }
        };

        animationFrame = requestAnimationFrame(step);

        return () => cancelAnimationFrame(animationFrame);
    }, [end, duration, suffix]);

    return <span ref={spanRef} className="tabular-nums">0{suffix}</span>;
}
