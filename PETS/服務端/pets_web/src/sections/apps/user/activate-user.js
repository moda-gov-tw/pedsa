import PropTypes from 'prop-types';
import { useContext, useState } from 'react';

// next
import { useSession } from 'next-auth/react';

// material-ui
import { Button, Dialog, DialogContent, DialogTitle, Stack, Typography } from '@mui/material';

// third-party
import axios from 'axios';

// project import
import Avatar from 'components/@extended/Avatar';
import { PopupTransition } from 'components/@extended/Transitions';

// assets
import PriorityHighIcon from '@mui/icons-material/PriorityHigh';
import {ConfigContext} from "../../../contexts/ConfigContext";
import petsLog from "../logger/insert-system-log";
import useUser from "../../../hooks/useUser";

// ==============================|| USER - ACTIVATE ||============================== //
/**
 * Function: AlertActivateDelete
 *
 * Child component of UserListTable
 *
 * @param {{ user: object, userId: number, userIsActive: boolean, allUsers: object, setAllUsers: func, open: bool, handleClose: func }} argObject
 * * `user`: value of current selected user.
 * * `userId`: value of current selected user id.
 * * `userIsActive`: value of selected user isactive.
 * * `allUsers`: list of all user(state).
 * * `setAllUsers`: function to update allUsers.
 * * `open`: control open/close of AlertGroupDelete.
 * * `onCancel`: function to control dialog open/close.
 *
 * @returns {JSX.Element}
 */
export default function AlertUserActivate({ user, userId, userIsActive, allUsers, setAllUsers, open, handleClose }) {
  const { data: session } = useSession();
  const loginUser = useUser();

  const [popUp, setPopUp] = useState(false);
  const [popUpMessage, setPopUpMessage] = useState('');
  const [wroteLog, setWroteLog] = useState({});
  let userNameToAction = '';
  if (user) {
      userNameToAction = user.useraccount;
  }

  // 更新人員列表裡的資料
  async function updateData() {
      let index = allUsers.findIndex(function(temp) {
          return temp.useraccount === user.useraccount;
      });
      let updatedUserData = {...allUsers[index], 'isactive': !allUsers[index].isactive};
      console.log('updatedUserData', updatedUserData);
      const newUserData = [
          ...allUsers.slice(0, index),
          updatedUserData,
          ...allUsers.slice(index+1)
      ];
      await setAllUsers(newUserData);
  }

  // 停權/復權人員
  async function handleActivate() {
      let url = '';
      if (userIsActive) {
          url = `/api/user/deactivate/${userId}`;
      }else {
          url = `/api/user/activate/${userId}`;
      }
      await axios.put(url,
          {},
          {
                    headers: {
                        Authorization: `Bearer ${session.tocken.loginUserToken}`
                    }
                })
          .then(async (response) => {
              console.log('activate/deactivate user success', response);
              await updateData();
              if(userIsActive) {
                  if (!wroteLog["deactivateUser"]) {
                      await petsLog(session, 0, `Login User ${loginUser.account}停權人員 ${userNameToAction} 成功`);
                      await setWroteLog(prev => ({ ...prev, ["deactivateUser"]: true }))
                  }
              } else {
                  console.log(wroteLog["activateUser"]);
                  if (!wroteLog["activateUser"]) {
                      await petsLog(session, 0, `Login User ${loginUser.account}復權人員 ${userNameToAction} 成功`);
                      await setWroteLog(prev => ({ ...prev, ["activateUser"]: true }))
                  }
              }
              await handleClose();
          })
          .catch(async (error) => {
              // console.log('delete user fail', error);
              if(userIsActive){
                  await setPopUpMessage('停權人員失敗');
                  if (!wroteLog["activateUser"]) {
                      await petsLog(session, 0, `Login User ${loginUser.account}停權人員 ${userNameToAction} 失敗`);
                      await setWroteLog(prev => ({ ...prev, ["activateUser"]: true }))
                  }
              }else {
                  await setPopUpMessage('復權人員失敗');
                  if (!wroteLog["deactivateUser"]) {
                      await petsLog(session, 0, `Login User ${loginUser.account}復權人員 ${userNameToAction} 失敗`);
                      setWroteLog(prev => ({ ...prev, ["deactivateUser"]: true }))
                  }
              }
              await setPopUp(true);
          });
  }

  async function handleClosePopUp() {
      await setPopUp(false);
  }

  return (
    <Dialog
      open={open}
      onClose={() => handleClose(false)}
      keepMounted
      TransitionComponent={PopupTransition}
      maxWidth="xs"
      aria-labelledby="column-delete-title"
      aria-describedby="column-delete-description"
    >
      {/*刪除確認視窗*/}
      <DialogContent sx={{ mt: 2, my: 1 }}>
        <Stack alignItems="center" spacing={3.5}>
          <Avatar color="error" sx={{ width: 72, height: 72, fontSize: '3rem' }}>
            <PriorityHighIcon/>
          </Avatar>
          <Stack spacing={2}>
            {(user && userIsActive) && (
                <Typography variant="h4" align="center">
                  確定停權人員{userNameToAction}嗎?
                </Typography>
            )}
            {(user && !userIsActive) && (
                <Typography variant="h4" align="center">
                  確定復權人員{userNameToAction}嗎?
                </Typography>
            )}
          </Stack>

          {/*確定/取消按鈕*/}
          <Stack direction="row" spacing={2} sx={{ width: 1 }}>
            <Button fullWidth onClick={() => handleClose(true)} color="secondary" variant="outlined">
              取消
            </Button>
            {(user && userIsActive) && (
                <Button fullWidth color="error" variant="contained" onClick={handleActivate} autoFocus>
                  停權
                </Button>
            )}
            {(user && !userIsActive) && (
                <Button fullWidth color="error" variant="contained" onClick={handleActivate} autoFocus>
                  復權
                </Button>
            )}
          </Stack>

          <Dialog open={popUp}>
            <DialogTitle>{popUpMessage}</DialogTitle>
            <Button onClick={handleClosePopUp}>確定</Button>
          </Dialog>
        </Stack>
      </DialogContent>
    </Dialog>
  );
}

AlertUserActivate.propTypes = {
    user: PropTypes.object,
    userId: PropTypes.number,
    allUsers: PropTypes.func,
    setAllUsers: PropTypes.func,
    handleClose: PropTypes.func
};
