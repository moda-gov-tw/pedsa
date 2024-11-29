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
import { DeleteFilled } from '@ant-design/icons';
import {ConfigContext} from "../../../contexts/ConfigContext";
import useUser from "../../../hooks/useUser";
import petsLog from "../logger/insert-system-log";

// ==============================|| USER - DELETE ||============================== //
/**
 * Function: AlertUserDelete
 *
 * Child component of UserListTable
 *
 * @param {{ user: object, userId: number, allUsers: object, setAllUsers: func, open: bool, handleClose: func }} argObject
 * * `user`: value of current selected user.
 * * `userId`: value of current selected user id.
 * * `allUsers`: list of all user(state).
 * * `setAllUsers`: function to update allUsers.
 * * `open`: control open/close of AlertGroupDelete.
 * * `onCancel`: function to control dialog open/close.
 *
 * @returns {JSX.Element}
 */
export default function AlertUserDelete({ user, userId, allUsers, setAllUsers, open, handleClose }) {
  const { data: session } = useSession();
  const loginUser = useUser();

  const [popUp, setPopUp] = useState(false);
  const [popUpMessage, setPopUpMessage] = useState('');
  const [wroteLog, setWroteLog] = useState({});
  let userNameToDelete = '';
  if (user) {
      userNameToDelete = user.useraccount;
  }

  // 更新人員列表裡的資料
  async function updateData() {
      let index = allUsers.findIndex(function(temp) {
          return temp.useraccount === user.useraccount;
      });
      const newUserData = [
          ...allUsers.slice(0, index),
          ...allUsers.slice(index+1)
      ];
      await setAllUsers(newUserData);
  }

  // 刪除人員
  async function handleDelete() {
      await axios.delete(`/api/user/delete/${userId}`,{
                    headers: {
                        Authorization: `Bearer ${session.tocken.loginUserToken}`
                    }
                })
          .then(async (response) => {
              // console.log('delete user success', response);
              await updateData();
              if (!wroteLog["deleteUser"]) {
                  await petsLog(session, 0, `Login User ${loginUser.account}刪除人員 ${userNameToDelete} 成功`);
                  setWroteLog(prev => ({ ...prev, ["deleteUser"]: true }))
              }
              await handleClose();
          })
          .catch(async (error) => {
              // console.log('delete user fail', error);
              await setPopUpMessage('刪除人員失敗，請檢查該人員是否離開所有專案，且該人員不能為單位管理員或專案管理員身份');
              if (!wroteLog["deleteUser"]) {
                  await petsLog(session, 0, `Login User ${loginUser.account}刪除人員 ${userNameToDelete} 失敗`);
                  setWroteLog(prev => ({ ...prev, ["deleteUser"]: true }))
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
          <Avatar color="error" sx={{ width: 72, height: 72, fontSize: '1.75rem' }}>
            <DeleteFilled />
          </Avatar>
          <Stack spacing={2}>
            <Typography variant="h4" align="center">
              確定刪除人員{userNameToDelete}嗎?
            </Typography>
          </Stack>

          {/*確定/取消按鈕*/}
          <Stack direction="row" spacing={2} sx={{ width: 1 }}>
            <Button fullWidth onClick={() => handleClose(true)} color="secondary" variant="outlined">
              取消
            </Button>
            <Button fullWidth color="error" variant="contained" onClick={handleDelete} autoFocus>
              刪除
            </Button>
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

AlertUserDelete.propTypes = {
    user: PropTypes.object,
    userId: PropTypes.number,
    allUsers: PropTypes.func,
    setAllUsers: PropTypes.func,
    handleClose: PropTypes.func
};
