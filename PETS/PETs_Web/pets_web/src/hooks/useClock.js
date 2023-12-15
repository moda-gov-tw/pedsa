// Turn function into `clock-functional component`.
import * as React from 'react';

/**
 * Function: useClock
 * 
 * A Moebius counter that updates the count every `delay` milliseconds and returns the current time.
 * 
 * @param {number} delay
 * - Milliseconds (thousandths of a second), timer should delay in between executions of the specified function or code.
 * @param {number} initialState
 * - The `initialState` as same as `useState` hook.
 * @param {number} finalState
 * - The final state of the clock.
 * @param {number} increaseStep
 * - The amount of increase from the current state to the next state.
 * @returns {number} current time (currentState) 
 */
// export default function useClock([state, setState], delay = 1000, initialState = 0, finalState = 60, increaseStep = 1) {
//     React.useEffect(() => {
//         const IntervalID = setInterval(() => {
//             setState((prevState) => (prevState >= finalState ? initialState : prevState + increaseStep));
//         }, delay);
//         return () => {
//             clearInterval(IntervalID);
//         };
//     }, []);
// }
export default function useClock({ initialState = -1, delay = 1000, restartState = 0, finalState = 60, increaseStep = 1 }) {
    const [state, setState] = React.useState(initialState);
    React.useEffect(() => {
        const IntervalID = setInterval(() => {
            setState((prevState) => (prevState >= finalState ? restartState : prevState + increaseStep));
        }, delay);
        return () => {
            clearInterval(IntervalID);
        };
    }, []);
    return [state];
}