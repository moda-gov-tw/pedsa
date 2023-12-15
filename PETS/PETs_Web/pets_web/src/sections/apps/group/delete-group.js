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
import useUser from "hooks/useUser";
import { PopupTransition } from 'components/@extended/Transitions';
import petsLog from "../logger/insert-system-log";

// assets
import { DeleteFilled } from '@ant-design/icons';
import {ConfigContext} from "../../../contexts/ConfigContext";


// ==============================|| GROUP - DELETE ||============================== //
/**
 * Function: AlertGroupDelete
 *
 * Child component of GroupListTable
 *
 * @param {{ group: object, groupId: number, allGroups: object, setAllGroups: func, open: bool, handleClose: func }} argObject
 * * `group`: value of current selected group.
 * * `groupId`: value of current selected group id.
 * * `allGroups`: list of all group(state).
 * * `setAllGroups`: function to update allGroups.
 * * `open`: control open/close of AlertGroupDelete.
 * * `onCancel`: function to control dialog open/close.
 *
 * @returns {JSX.Element}
 */
export default function AlertGroupDelete({ group, groupId, allGroups, setAllGroups, open, handleClose }) {
  const { data: session } = useSession();
  const user = useUser();

  const [popUp, setPopUp] = useState(false);
  const [popUpMessage, setPopUpMessage] = useState('');
  const [wroteLog, setWroteLog] = useState({});
  let groupNameToDelete = '';
  if (group) {
      groupNameToDelete = group.group_name;
  }

  // 更新單位列表裡的資料
  async function updateData() {
      let index = allGroups.findIndex(function(temp) {
          return temp.group_name === group.group_name;
      });
      const newGroupData = [
          ...allGroups.slice(0, index),
          ...allGroups.slice(index+1)
      ];
      await setAllGroups(newGroupData);
  }

  // 刪除單位
  async function handleDelete() {
      await axios.delete(`/api/group/delete/${groupId}`,{
                    headers: {
                        Authorization: `Bearer ${session.tocken.loginUserToken}`
                    }
                })
          .then(async (response) => {
              console.log('delete group success', response);
              await updateData();
              await handleClose();
              if (!wroteLog["deleteGroup"]) {
                  await petsLog(session, 0, `Login User ${user.account}刪除單位${groupNameToDelete}成功`);
                  setWroteLog(prev => ({ ...prev, ["deleteGroup"]: true }))
              }
          })
          .catch(async (error) => {
              console.log('delete group fail', error);
              await setPopUpMessage('刪除單位失敗，請檢查單位是否存在');
              if (!wroteLog["deleteGroup"]) {
                  await petsLog(session, 0, `Login User ${user.account}刪除單位${groupNameToDelete}失敗`);
                  setWroteLog(prev => ({ ...prev, ["deleteGroup"]: true }))
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
              確定刪除單位{groupNameToDelete}嗎?
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

AlertGroupDelete.propTypes = {
    group: PropTypes.object,
    groupId: PropTypes.number,
    allGroups: PropTypes.func,
    setAllGroups: PropTypes.func,
    handleClose: PropTypes.func
};
