import React from 'react';
import {
    Box,
    Button,
    Dialog,
    DialogActions,
    DialogContent,
    DialogContentText,
    DialogTitle,
    MenuItem
} from '@mui/material';

export default function CustomAlertDialog({
    buttonType = "Button",
    buttonVariant = "div",
    buttonText = "button",

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
    const [open, setOpen] = React.useState(false);

    const handleClickOpen = () => {
        setOpen(true);
    };

    const handleClose = () => {
        setOpen(false);
    };

    if (!disagreeButtonOnClick) disagreeButtonOnClick = handleClose;
    if (!agreeButtonOnClick) agreeButtonOnClick = handleClose;

    // Content change line
    const splitContent = dialogContent.split("\n");
    const newContent = [splitContent[0]];
    for (let i = 1; i < splitContent.length; i++) {
        newContent.push(<br />, splitContent[i]);
    }

    // Button Component
    const triggerButton = () => {
        if (buttonType == "MenuItem") {
            return (
                <MenuItem variant={(buttonVariant) ? buttonVariant : null} onClick={handleClickOpen} textAlign="left" sx={{ borderRadius: 0 }}>
                    {buttonText}
                </MenuItem>
            );
        }
        else {
            return (
                <Button variant={(buttonVariant) ? buttonVariant : null} onClick={handleClickOpen} textAlign="left" sx={{ borderRadius: 0 }}>
                    {buttonText}
                </Button>
            );
        }
    }

    return (
        <>
            {triggerButton()}
            <Dialog open={open} onClose={handleClose} aria-labelledby="alert-dialog-title" aria-describedby="alert-dialog-description">
                <Box sx={{ p: 1, py: 1.5 }}>
                    <DialogTitle id="alert-dialog-title" textAlign="center" ><b>{dialogTitle}</b></DialogTitle>
                    <DialogContent>
                        <DialogContentText id="alert-dialog-description" textAlign="center">
                            {newContent}
                        </DialogContentText>
                    </DialogContent>
                    <Box sx={{ display: "flex", justifyContent: "center" }}>
                        <DialogActions>
                            <Button variant={disagreeButtonVariant} color={disagreeButtonColor} onClick={disagreeButtonOnClick} >
                                {disagreeButtonText}
                            </Button>
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
