import PropTypes from 'prop-types';
import { useContext, useEffect, useMemo, useState } from 'react';
import * as React from 'react';

// next
import { useSession, } from 'next-auth/react';
import { useRouter } from 'next/router';

// material-ui
import { useTheme } from '@mui/material/styles';
import {
    Box,
    Button,
    Divider,
    Grid,
    Stack,
    Typography,
    Step,
    Stepper,
    StepLabel,
    StepNumber,
    styled,
} from '@mui/material';
import StepConnector, { stepConnectorClasses } from '@mui/material/StepConnector';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CircleIcon from '@mui/icons-material/Circle';

// third-party
import axios from 'axios';

// project import
import Layout from 'layout';
import Page from 'components/Page';

const QontoConnector = styled(StepConnector)(({ theme }) => ({
    [`&.${stepConnectorClasses.alternativeLabel}`]: {
        top: 10,
        left: 'calc(-50% + 16px)',
        right: 'calc(50% + 16px)',
    },
    [`&.${stepConnectorClasses.active}`]: {
        [`& .${stepConnectorClasses.line}`]: {
            borderColor: theme.palette.primary.main,
        },
    },
    [`&.${stepConnectorClasses.completed}`]: {
        [`& .${stepConnectorClasses.line}`]: {
            borderColor: theme.palette.primary.main,
        },
    },
    [`& .${stepConnectorClasses.line}`]: {
        borderColor: theme.palette.mode === 'dark' ? theme.palette.grey[400] : theme.palette.grey[500],
        borderTopWidth: 3,
        borderRadius: 1,
    },
}));

const QontoStepIconRoot = styled('div')(({ theme, ownerState }) => ({
    color: theme.palette.mode === 'dark' ? theme.palette.grey[400] : theme.palette.grey[500],
    display: 'flex',
    height: 22,
    alignItems: 'center',
    ...(ownerState.active && {
        color: theme.palette.primary.main,
    }),
    '& .QontoStepIcon-completedIcon': {
        color: theme.palette.primary.main,
        zIndex: 1,
        // fontSize: 18,
        width: 13,
        height: 13,
        borderRadius: '50%',
        backgroundColor: 'currentColor', // circle
    },
    '& .QontoStepIcon-circle': {
        width: 13,
        height: 13,
        borderRadius: '50%',
        backgroundColor: 'currentColor', // circle
    },
}));

function QontoStepIcon(props) {
    const { active, completed, className } = props;

    return (
        <QontoStepIconRoot ownerState={{ active }} className={className}>
            {completed ? (
                // <CheckCircleIcon className="QontoStepIcon-completedIcon" />
                <div className="QontoStepIcon-completedIcon" />
            ) : (
                <div className="QontoStepIcon-circle" />
            )}
        </QontoStepIconRoot>
    );
}

QontoStepIcon.propTypes = {
    /**
     * Whether this step is active.
     * @default false
     */
    active: PropTypes.bool,
    className: PropTypes.string,
    /**
     * Mark the step as completed. Is passed to child components.
     * @default false
     */
    completed: PropTypes.bool,
};

/**
 * Function: GeneralStepper
 *
 * @param {{ currentStep:number, terminatedStep:number, StepNameMapping:object, StepName:String }} argObject
 * * `currentStep`: value of current step (-1 ~ terminatedStep).
 * * `terminatedStep`: value of final stap.
 * * `StepNameMapping`: status names.
 * * `StepName`: Direct use `StepName`, don't care `StepNameMapping`.
 * @returns {JSX.Element}
 */
export default function GeneralStepper({ currentStep = 2, terminatedStep = 5, StepNameMapping = {}, StepName = null }) {
    // console.log('GeneralStepper', currentStep, terminatedStep);
    const steps = Array.from({ length: terminatedStep }, (v, i) => i);

    const show_stepper = () => (
        <>
            <Stepper activeStep={currentStep} alternativeLabel connector={<QontoConnector />} >
                {steps.map((label) => (
                    <Step key={label}>
                        <StepLabel StepIconComponent={QontoStepIcon}>{/*text*/}</StepLabel>
                    </Step>
                ))}
            </Stepper>
            {(StepName == null) ?
                <>
                    <Box sx={{ display: "flex", justifyContent: "center", alignItems: "center" }}>
                        <Typography variant='h5'>{StepNameMapping[currentStep]}</Typography>
                    </Box>
                </> : <>
                    <Box sx={{ display: "flex", justifyContent: "center", alignItems: "center" }}>
                        <Typography variant='h5'>{StepName}</Typography>
                    </Box>
                </>}

        </>
    );


    // Return rendered elements
    return (show_stepper());
}