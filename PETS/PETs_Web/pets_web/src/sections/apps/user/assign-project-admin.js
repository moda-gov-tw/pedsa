import PropTypes from 'prop-types';
import {useContext, useEffect, useState} from 'react';

// next
import { useSession } from 'next-auth/react';

// material-ui
import { Button, Dialog, DialogContent, DialogTitle, Stack, Typography } from '@mui/material';

// third-party
import axios from 'axios';

// project import
import Avatar from 'components/@extended/Avatar';
import { PopupTransition } from 'components/@extended/Transitions';
import petsLog from 'sections/apps/logger/insert-system-log';

// assets
import { DeleteFilled } from '@ant-design/icons';
import {ConfigContext} from "../../../contexts/ConfigContext";
import {system_roles_dic} from "../../../data/member-role";
import useUser from "hooks/useUser";

// ==============================|| USER - ASSIGN TO PROJECT ADMIN ||============================== //
/**
 * Function: AssignUserProjectAdmin
 *
 * Child component of UserListTable
 *
 * @param {{ user: object, userId: number, userIsProjectAdmin: boolean, userProjectAdminId: number, allUsers: object, setAllUsers: func, open: bool, handleClose: func }} argObject
 * * `user`: value of current selected user.
 * * `userId`: value of current selected user id.
 * * `userIsProjectAdmin`: value of selected user is project admin or not.
 * * `userProjectAdminId： value of selected user project admin role_id.
 * * `allUsers`: list of all user(state).
 * * `setAllUsers`: function to update allUsers.
 * * `open`: control open/close of AlertGroupDelete.
 * * `onCancel`: function to control dialog open/close.
 *
 * @returns {JSX.Element}
 */
export default function AssignUserProjectAdmin({ user, userId, userIsProjectAdmin, userProjectAdminId, allUsers, setAllUsers, open, handleClose }) {
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

      let updatedUserData = {...allUsers[index], 'is_project_admin': {status: !allUsers[index].is_project_admin.status}};
      const newUserData = [
          ...allUsers.slice(0, index),
          updatedUserData,
          ...allUsers.slice(index+1)
      ];
      await setAllUsers(newUserData);
  }

  // 停權/復權人員
  async function handleAssignProjectAdmin() {
      let url = '';
      if (!userIsProjectAdmin) {
          url = `/api/role/put_setAdmin`;
          await axios.post(url,
          {member_id: userId, role_name: 'project_admin'},
          {
                    headers: {
                        Authorization: `Bearer ${session.tocken.loginUserToken}`
                    }
                })
          .then(async (response) => {
              console.log('add to project admin success', response);
              await updateData();
              if (!wroteLog["assignUserProjectAdmin"]) {
                  await petsLog(session, 0, `Login User ${loginUser.account} 設定人員(id${userId}) 為專案管理員成功`);
                  setWroteLog(prev => ({ ...prev, ["assignUserProjectAdmin"]: true }));
              }
              await handleClose();
          })
          .catch(async (error) => {
              console.log('add to project admin fail', error);
              await setPopUpMessage('指派人員為專案管理員失敗，請確認人員已啟用');
              if (!wroteLog["assignUserProjectAdmin"]) {
                  await petsLog(session, 0, `Login User ${loginUser.account} 設定人員(id${userId}) 為專案管理員失敗`);
                  setWroteLog(prev => ({ ...prev, ["assignUserProjectAdmin"]: true }))
              }
              await setPopUp(true);
          });
      }else {
          let role_id = userProjectAdminId;
          url = `/api/role/delete_deleteAdmin/${role_id}`;
          await axios.delete(url,
          {
                    headers: {
                        Authorization: `Bearer ${session.tocken.loginUserToken}`
                    }
                })
          .then(async (response) => {
              console.log('remove project admin success', response);
              await updateData();
              if (!wroteLog["removeUserProjectAdmin"]) {
                  await petsLog(session, 0, `Login User ${loginUser.account} 移除人員(id${userId}) 為專案管理員成功`);
                  setWroteLog(prev => ({ ...prev, ["removeUserProjectAdmin"]: true }))
              }
              await handleClose();
          })
          .catch(async (error) => {
              console.log('remove project admin fail', error);
              await setPopUpMessage('指派人員為專案管理員失敗');
              if (!wroteLog["removeUserProjectAdmin"]) {
                  await petsLog(session, 0, `Login User ${loginUser.account} 移除人員(id${userId}) 為專案管理員失敗`);
                  setWroteLog(prev => ({ ...prev, ["removeUserProjectAdmin"]: true }))
              }
              await setPopUp(true);
          });

      }

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
      {/*指派為專案管理員確認視窗*/}
      <DialogContent sx={{ mt: 2, my: 1 }}>
        <Stack alignItems="center" spacing={3.5}>
          {/*<Avatar color="error" sx={{ width: 72, height: 72, fontSize: '1.75rem' }}>*/}
          {/*  <DeleteFilled />*/}
          {/*</Avatar>*/}
          <Stack spacing={2}>
            {(user && userIsProjectAdmin) && (
                <Typography variant="h4" align="center">
                  確定移除人員{userNameToAction}專案管理員嗎?
                </Typography>
            )}
            {(user && !userIsProjectAdmin) && (
                <Typography variant="h4" align="center">
                  確定新增人員{userNameToAction}為專案管理員嗎?
                </Typography>
            )}
          </Stack>

          {/*確定/取消按鈕*/}
          <Stack direction="row" spacing={2} sx={{ width: 1 }}>
            <Button fullWidth onClick={() => handleClose(true)} color="secondary" variant="outlined">
              取消
            </Button>
            {(user && userIsProjectAdmin) && (
                <Button fullWidth color="error" variant="contained" onClick={handleAssignProjectAdmin} autoFocus>
                  移除
                </Button>
            )}
            {(user && !userIsProjectAdmin) && (
                <Button fullWidth color="error" variant="contained" onClick={handleAssignProjectAdmin} autoFocus>
                  新增
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

AssignUserProjectAdmin.propTypes = {
    user: PropTypes.object,
    userId: PropTypes.number,
    allUsers: PropTypes.func,
    setAllUsers: PropTypes.func,
    handleClose: PropTypes.func
};
