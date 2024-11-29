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

// third-party
import axios from 'axios';

// project import
import Layout from 'layout';
import Page from 'components/Page';

// Stepper: Horizontal dash
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
        borderColor: theme.palette.mode === 'dark' ? theme.palette.grey[600] : theme.palette.grey[600],
        borderTopWidth: 3,
        borderRadius: 1,
    },
}));

// Stepper: Circle
const StepMarkerIconRoot = styled('div')(({ theme, ownerState }) => ({
    color: ownerState.active ? 'red' : theme.palette.mode === 'dark' ? theme.palette.grey[500] : theme.palette.grey[500],
    display: 'flex',
    height: 22,
    alignItems: 'center',
    // active circle (include current status)
    '& .StepMarkerIcon-activeIcon': {
        color: theme.palette.primary.main,
        zIndex: 1,
        fontSize: 18,
    },
    // complete circle
    '& .StepMarkerIcon-completedIcon': {
        color: theme.palette.primary.main,
        zIndex: 1,
        fontSize: 18,
    },
    // inactivae circle
    '& .StepMarkerIcon-circle': {
        width: 13,
        height: 13,
        borderRadius: '50%',
        backgroundColor: 'currentColor',
    },
}));

function StepMarkerIcon(props) {
    const { active, completed, className } = props;

    return (
        <StepMarkerIconRoot ownerState={{ active }} className={className}>
            {(active) ? (
                <CheckCircleIcon className="StepMarkerIcon-activeIcon" />
            ) : (completed) ? (
                <CheckCircleIcon className="StepMarkerIcon-completedIcon" />
            ) : (
                <div className="StepMarkerIcon-circle" />
            )}
        </StepMarkerIconRoot>
    );
}

StepMarkerIcon.propTypes = {
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


function mapStateToNewState(status, mappingTable) {
    // Example of mappingTable //
    // const mappingTable = [
    //     { range: [1, 3], newState: 1 },
    //     { range: [4, 8], newState: 2 },
    //     // Add more ranges and new status here
    // ];

    // Binary Search
    let left = 0;
    let right = mappingTable.length - 1;

    while (left <= right) {
        const mid = Math.floor((left + right) / 2);
        const { range, newState } = mappingTable[mid];

        if (status >= range[0] && status <= range[1]) {
            return newState;
        } else if (status < range[0]) {
            right = mid - 1;
        } else {
            left = mid + 1;
        }
    }

    // Return null if the status is not in any range
    return null;
}


/**
 * Function: ProjectStepper
 *
 * @param {{ currentStep:number, terminatedStep:number }} argObject
 * * `currentStep`: value of current step (-1 ~ terminatedStep).
 * * `terminatedStep`: value of final stap.
 * @returns {JSX.Element}
 */
export default function ProjectStepper({ currentStep = 2, terminatedStep = 5 }) {
    //console.log('ProjectStepper', currentStep, terminatedStep);
    const mapStatusBackend2Frontend = [
        { range: [-2, -1], newState: -1 },
        { range: [0, 1], newState: 0 },
        { range: [2, 2], newState: 1 },
        { range: [3, 3], newState: 2 },
        { range: [4, 5], newState: 3 },
        { range: [6, 9], newState: 4 },
    ];
    const StepNameMapping = {
        '-1': '',
        '0': '專案建立與設定',
        '1': '資料匯入及鏈結檢查',
        '2': '資料鏈結處理',
        '3': '隱私強化機制選擇',
        '4': '隱私強化資料產生',
    }

    // console.log("StepNameMapping.length", Object.keys(StepNameMapping).length);

    const steps = Array.from({ length: (terminatedStep) ? terminatedStep : (Object.keys(StepNameMapping).length - 1) }, (v, i) => i);

    // Process status mapping 
    const backendStatus = currentStep;
    const frontendStatus = mapStateToNewState(backendStatus, mapStatusBackend2Frontend)

    // Return rendered elements
    return (
        <>
            <Stepper activeStep={frontendStatus} alternativeLabel connector={<QontoConnector />} >
                {steps.map((label, index) => (
                    <Step key={label}>
                        <StepLabel StepIconComponent={StepMarkerIcon}>{StepNameMapping[String(label)]}</StepLabel>
                    </Step>
                ))}
            </Stepper>
        </>
    );
}
