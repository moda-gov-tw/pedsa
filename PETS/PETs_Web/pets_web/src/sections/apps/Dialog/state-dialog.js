import React from 'react';
import {
    Box,
    Button,
    Dialog,
    DialogActions,
    DialogContent,
    DialogContentText,
    DialogTitle
} from '@mui/material';

export default function StateControlDialog({
    stateArrayOpenControl = [open, setOpen],
    disagreeButtonVariant,
    disagreeButtonColor,
    disagreeButtonOnClick,
    disagreeButtonText = "Disagree",

    agreeButtonVariant = "contained",
    agreeButtonColor,
    agreeButtonOnClick,
    agreeButtonText = "Agree",

    dialogTitle = "Title",
    dialogContent = "Hello world!",
}) {
    const [open, setOpen] = stateArrayOpenControl;

    const handleClose = (e) => {
        setOpen(false);
    };

    if (!disagreeButtonOnClick) disagreeButtonOnClick = handleClose;
    if (!agreeButtonOnClick) agreeButtonOnClick = handleClose;

    // Content change line
    const newContent = [];
    if (dialogContent) {
        const splitContent = dialogContent.split("<br>");
        console.log(splitContent, splitContent);
        newContent.push(splitContent[0]);
        for (let i = 1; i < splitContent.length; i++) {
            newContent.push(<br />, splitContent[i]);
        }
    }

    return (
        <>
            <Dialog open={open} onClose={handleClose} aria-labelledby="alert-dialog-title" aria-describedby="alert-dialog-description">
                <Box sx={{ p: 1, py: 1.5 }}>
                    <DialogTitle id="alert-dialog-title" textAlign="center" ><b>{dialogTitle}</b></DialogTitle>
                    {(newContent.length > 0) ?
                        <>
                            <DialogContent>
                                <DialogContentText id="alert-dialog-description" textAlign="center">
                                    {newContent}
                                </DialogContentText>
                            </DialogContent>
                        </> : <></>}
                    <Box sx={{ display: "flex", justifyContent: "center" }}>
                        <DialogActions>
                            {(disagreeButtonText) ?
                                <Button variant={disagreeButtonVariant} color={disagreeButtonColor} onClick={disagreeButtonOnClick} >
                                    {disagreeButtonText}
                                </Button> : <></>
                            }
                            <Button variant={agreeButtonVariant} color={agreeButtonColor} onClick={agreeButtonOnClick}>
                                {agreeButtonText}
                            </Button>
                        </DialogActions>
                    </Box>
                </Box>
            </Dialog>
        </>
    );
}
