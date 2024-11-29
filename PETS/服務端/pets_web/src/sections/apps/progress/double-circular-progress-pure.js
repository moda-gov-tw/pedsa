import * as React from 'react';
import { useMemo } from 'react';
import PropTypes from 'prop-types';

// material-ui
import {
    Box,
    Typography,
} from '@mui/material'
import CircularProgress, {
    circularProgressClasses,
} from '@mui/material/CircularProgress';

/**
 * Function: FakeCircularLoadingAnimation
 * 
 * Child compoent of `DoubleCircularProgressPure`
 * 
 * @param {{ size: number, animationDuration: string }} props 
 * * `size`: The size of the `<CircularProgress>`.
 * * `animationDuration`: The animation duration of the `<CircularProgress>`.
 * @returns {JSX.Element}
 */
function FakeCircularLoadingAnimation(props) {
    return (
        <>
            {/* background grey circle */}
            <CircularProgress
                variant="determinate"
                sx={{
                    color: (theme) =>
                        theme.palette.grey[theme.palette.mode === 'light' ? 200 : 800],
                    position: 'absolute',
                }}
                size={props.size}
                thickness={0.5}
                value={100}
            //{...props}
            />
            {/* dynamic blue circle */}
            <CircularProgress
                variant="indeterminate"
                disableShrink
                sx={{
                    color: (theme) => (theme.palette.mode === 'light' ? theme.palette.primary.secondary : theme.palette.secondary.secondary),
                    animationDuration: props.animationDuration,
                    [`& .${circularProgressClasses.circle}`]: {
                        strokeLinecap: 'round',
                    },
                    position: 'absolute',
                }}
                size={props.size}
                thickness={1}
            //{...props}
            />

            {/* Inner Text */}
            <>
                {(props.showText) ?
                    <Box
                        sx={{
                            top: 0,
                            left: 0,
                            bottom: 0,
                            right: 0,
                            position: 'absolute',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                        }}
                    >
                        <Typography variant="h6" component="div" color="text.primary" fontWeight="bold">
                            {`資料處理中，請稍後...`}
                        </Typography>
                    </Box>
                    : ""}
            </>
        </>
    )
}

/**
 * Function: RealtimeCircularProgress
 * 
 * Child compoent of `DoubleCircularProgressPure`
 * 
 * @param {{ value: number, size: number }} props 
 * * `value`: The progress value of the `<CircularProgress>`.
 * * `size`: The size of the `<CircularProgress>`.
 * @returns {JSX.Element}
 */
function RealtimeCircularProgress(props) {
    const ShowProgressText = (progress) => {
        if (progress < 100)
            return (
                <Typography variant="h4" component="div" color="text.secondary">
                    {`安全資料鏈結處理中 ${Math.round(progress)}%`}
                </Typography>
            );
        else
            return (
                <Typography variant="h4" component="div" color="text.secondary">
                    {`已完成 ${Math.round(progress)}%`}
                </Typography>
            );
    }

    return (
        <Box sx={{ position: 'relative', }}>
            {/* background grey circle */}
            <CircularProgress
                variant="determinate"
                sx={{
                    color: (theme) =>
                        theme.palette.grey[theme.palette.mode === 'light' ? 200 : 800],
                    position: 'absolute',
                }}
                size={props.size}
                thickness={0.3}
                value={100}
            />
            {/* dynamic blue circle */}
            <CircularProgress variant="determinate"
                sx={{ color: (theme) => theme.palette.primary.main }}
                size={props.size}
                thickness={1}
                value={props.value}
            />
            {/* progress text */}
            <Box
                sx={{
                    top: 0,
                    left: 0,
                    bottom: 0,
                    right: 0,
                    position: 'absolute',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                }}
            >
                {ShowProgressText(props.value)}
            </Box>
        </Box>
    );
}

RealtimeCircularProgress.propTypes = {
    /**
     * The value of the progress indicator for the determinate variant.
     * Value between 0 and 100.
     * @default 0
     */
    value: PropTypes.number.isRequired,
};



/**
 * Function: DoubleCircularProgressPure
 * 
 * @param {{ value:number, innerCicleSize:number, outerCicleSize:number, animationDuration:string, animationDurationOutter:string }} argObject
 * * `value`: The progress value of the `<CircularProgress>`.
 * * `innerCicleSize`: The size of inner circle.
 * * `outerCicleSize`: The size of outer circle.
 * * `animationDuration`: The rotation duration of inner circle.
 * * `animationDurationOutter`: The rotation duration of outter circle.
 * @returns {JSX.Element}
 */
export default function DoubleCircularProgressPure({ value = 50, innerCicleSize = 250, outerCicleSize = 300, animationDuration = '550ms', animationDurationOutter = '400ms' }) {
    //console.log('DoubleCircularProgressPure', value);

    // Return rendered elements
    return (
        // `flexGrow` automatically fills the remaining space in the flex container
        <Box sx={{ flexGrow: 1 }}>
            <Box sx={{
                height: '100%',
                top: 0,
                left: 0,
                bottom: 0,
                right: 0,
                margin: '5%',
                position: 'relative',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
            }} >
                {/* inner circle */}
                <FakeCircularLoadingAnimation size={innerCicleSize} animationDuration={animationDuration} />
                {/* outer circle */}
                <FakeCircularLoadingAnimation size={outerCicleSize} animationDuration={animationDurationOutter} showText={true} />
            </Box>
        </Box>
    );
}
