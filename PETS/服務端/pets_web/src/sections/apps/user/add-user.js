import PropTypes from 'prop-types';
import { useContext, useState, useEffect } from 'react';
import { useDispatch } from 'react-redux';

// next
import { useSession } from 'next-auth/react';

// material-ui
import {
  Button,
  Checkbox,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Divider,
  FormControlLabel,
  FormGroup,
  Grid,
  InputLabel,
  IconButton,
  MenuItem,
  Select,
  Stack,
  Tooltip,
  TextField,
} from '@mui/material';
import { LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import CheckIcon from '@mui/icons-material/Check';

// third-party
import axios from 'axios';
import _ from 'lodash';
import * as Yup from 'yup';
import { useFormik, Form, FormikProvider } from 'formik';

// project imports
import { openSnackbar } from 'store/reducers/snackbar';
import petsLog from 'sections/apps/logger/insert-system-log';
// import { mockGroupList } from 'utils/mock-groups';
import { checkEmail, checkEmailMsg, checkUseraccount, checkUsername } from 'utils/check-rules';
import StateControlDialog from '../Dialog/state-dialog';

// assets
import { ConfigContext } from "contexts/ConfigContext";
import { system_roles, system_roles_dic } from "data/member-role";
import getALLGroups from "utils/getGroups";
import useUser from "../../../hooks/useUser";

// constant
const getInitialValues = (user) => {
  const newUser = {
    username: '',
    email: '@',
    group_name: '',
    role: [],
  };
  if (user) {
    // console.log('m', _.merge({}, newUser, user));
    return _.merge({}, newUser, user);
  }
  // console.log('newUser', newUser);
  return newUser;
};

// ==============================|| USER ADD / EDIT / DELETE ||============================== //
/**
 * Function: AddUser
 *
 * Child component of UserListTable
 *
 * @param {{ user: object, userId: number, userAdminRoles: object, allUsers: object, setAllUsers: func, onCancel: func }} argObject
 * * `user`: value of current selected user.
 * * `userId`: value of current selected user id.
 * * `userAdminRoles`: value of current selected user admin roles.
 * * `allUsers`: list of all user(state).
 * * `setAllUsers`: function to update allUsers.
 * * `onCancel`: function to control dialog open/close.
 *
 * @returns {JSX.Element}
 */
const AddUser = ({ user, userId, userAdminRoles, allUsers, setAllUsers, onCancel, onUpdate }) => {
  const { data: session } = useSession();
  const loginUser = useUser();
  const CancelToken = axios.CancelToken;
  const source = CancelToken.source();

  const dispatch = useDispatch();
  const { allGroups, setAllGroups, userPermission } = useContext(ConfigContext); // 所有單位
  const [userInfo, setUserInfo] = useState(null);
  const [popUp, setPopUp] = useState(false);
  const [checkPopUp, setCheckPopUp] = useState(false);
  const [newUserPopup, setNewUserPopup] = useState(false);
  const [popUpMessage, setPopUpMessage] = useState('');
  const [wroteLog, setWroteLog] = useState({});
  const [copied, setCopied] = useState(false);

  const UserSchema = Yup.object().shape({
    username: Yup.string(),
    email: Yup.string(),
    group_name: Yup.string(),
  });

  function checkNotEmpty() {
    if (values.group_name === '' || values.useraccount === '' || values.username === '' || values.email === '') {
      return false;
    }
    return true;
  }

  function checkValid() {
    if (checkUseraccount(values.useraccount) || checkUsername(values.username) || !checkEmail(values.email)) {
      return false;
    }
    return true;
  }

  const checkSubmitValues = async () => {
    const r1 = await checkNotEmpty();
    const r2 = await checkValid();
    return (r1 && r2);
  };

  const formik = useFormik({
    initialValues: getInitialValues(user),
    validationSchema: UserSchema,
    onSubmit: async (values, { setSubmitting }) => {
      try {
        if (user) {
          await setPopUpMessage('編輯人員中');
          // await setPopUp(true);
          dispatch(
            openSnackbar({
              open: true,
              message: '檢查編輯人員資訊中',
              variant: 'alert',
              alert: {
                color: 'success'
              },
              close: false
            })
          );
        } else {
          await setPopUpMessage('檢查新增人員資訊中');
          // await setPopUp(true);
          dispatch(
            openSnackbar({
              open: true,
              message: '檢查新增人員資訊中',
              variant: 'alert',
              alert: {
                color: 'success'
              },
              close: false
            })
          );
        }
        // console.log('submit values', values);
        if (user) {
          const checkResult = await checkSubmitValues();
          if (checkResult) {
            await setPopUpMessage('編輯人員中');
            await setPopUp(true);
            await handleEditUser();
            if (!wroteLog["editUser"]) {
              await petsLog(session, 0, `Login User ${loginUser.account} 編輯人員${values.useraccount} 成功`);
              setWroteLog(prev => ({ ...prev, ["editUser"]: true }))
            }
          } else {
            await setPopUpMessage('請確認帳號、姓名、信箱皆有填入值，且符合對應格式');
            await setCheckPopUp(true);
          }
        } else {
          const checkResult = await checkSubmitValues();
          if (checkResult) {
            await setPopUpMessage('新增人員中');
            await setPopUp(true);
            await handleCreateUser();
            if (!wroteLog["addUser"]) {
              await petsLog(session, 0, `Login User ${loginUser.account} 新增人員${values.useraccount} 成功`);
              setWroteLog(prev => ({ ...prev, ["addUser"]: true }))
            }
          } else {
            await setPopUpMessage('請確認帳號、姓名、信箱皆有填入值，且符合對應格式');
            await setCheckPopUp(true);
          }
        }
        setSubmitting(false);
      } catch (error) {
        // console.error(error);
      }
    }
  });
  const { values, errors, touched, handleSubmit, isSubmitting, getFieldProps, setFieldValue } = formik;

  useEffect(() => {
    // 取得所有機關
    getALLGroups(setAllGroups, session.tocken.loginUserToken);
  }, []);

  let oriAdminRoles = userAdminRoles;

  useEffect(() => {
    if (user) {
      setFieldValue('role', userAdminRoles);
    }
  }, []);

  // 取得使用者資訊
  const getUserInfo = async (token) => {
    // console.log('getUserInfo');
    await axios.get(`/api/user/get_info/${userId}`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
      .then((response) => {
        // console.log('get user info', response.data.obj);
        setUserInfo(response.data.obj);
        let info = response.data.obj;
        setFieldValue('group_name', `${info.group_id}_${info.group_type}_${info.group_name}`)
      })
      .catch((error) => {
        // console.log('get user info error', error);
      });
  };

  useEffect(() => {
    // 取得使用者資訊
    if (user) {
      getUserInfo(session.tocken.loginUserToken);
    }
  }, []);

  // 新增人員列表資料
  async function appendData(newUserData, newUserId) {
    let groupInfo = newUserData['group_name'];
    newUserData['id'] = newUserId;
    newUserData['isactive'] = true;
    newUserData['ischange'] = false;
    // 單位
    newUserData['group_id'] = groupInfo.split('_')[0];
    newUserData['group_type'] = groupInfo.split('_')[1];
    newUserData['group_name'] = groupInfo.split('_')[2];
    // 角色
    newUserData['is_super_admin'] = false;
    newUserData['is_group_admin'] = false;
    newUserData['is_project_admin'] = { 'status': false };
    // console.log('newUserData', newUserData);
    await setAllUsers([...allUsers, { ...newUserData }]);
  }

  // 更新人員列表資料
  async function updateData(newUserData, admin_roles) {
    let groupInfo = newUserData['group_name'];
    let index = allUsers.findIndex(function (temp) {
      return temp.username === user.username;
    });
    let updatedUserData = { ...allUsers[index], ...newUserData };
    // 單位
    updatedUserData['group_name'] = groupInfo.split('_')[2];
    // 角色
    updatedUserData['is_super_admin'] = admin_roles.includes('系統管理員');
    updatedUserData['is_group_admin'] = admin_roles.includes('單位管理員');
    updatedUserData['is_project_admin'] = { 'status': admin_roles.includes('專案管理員') };
    // console.log('updatedUserData', updatedUserData);
    const newAllUsers = [
      ...allUsers.slice(0, index),
      updatedUserData,
      ...allUsers.slice(index + 1)
    ];
    await setAllUsers(newAllUsers);
    await onUpdate();
  }

  // 複製密碼
  const handleCopyClick = (event, text) => {
    navigator.clipboard.writeText(text).then(() => {
      // console.log('Text copied to clipboard');
      setCopied(true);
      dispatch(
        openSnackbar({
          open: true,
          message: '複製成功',
          variant: 'alert',
          alert: {
            color: 'success'
          },
          close: false
        })
      );
      setTimeout(() => {
        setCopied(false);
      }, 2000);
    }).catch(err => {
      // console.error('Could not copy text: ', err);
    });
  };

  // 新增人員
  async function handleCreateUser() {
    const newUserPayload = {
      'useraccount': values.useraccount.trim(),
      'username': values.username.trim(),
      'email': values.email.trim(),
      'group_id': values.group_name.split('_')[0],
      'ischange': false,
    }
    // console.log("new user payload",newUserPayload)
    await axios.post('/api/user/create_user/', newUserPayload,
      {
        headers: {
          Authorization: `Bearer ${session.tocken.loginUserToken}`
        }
      })
      .then(async (response) => {
        // await setPopUpMessage(`新增人員成功，預設密碼為: ${response.data.obj.default_password}123###`+ '複製密碼'+ <ContentCopyIcon/> + '複製密碼');
        await setPopUpMessage(
          <div>
            新增人員成功，預設密碼為: {response.data.obj.default_password}
            <Tooltip title="複製密碼" placement="top">
              <IconButton
                onClick={(event) => {
                  handleCopyClick(event, response.data.obj.default_password);
                }}
              >
                {copied ? <CheckIcon /> : <ContentCopyIcon />}
              </IconButton>
            </Tooltip>
          </div>
        );
        await setNewUserPopup(true);
        await appendData(values, response.data.obj.member_id);
        await onUpdate();
        // await onCancel();
      })
      .catch(async (error) => {
        // console.log('add error');
        await setPopUpMessage(`新增人員失敗，請確認人員是否已存在`);
        await setNewUserPopup(true);
        // console.log('error', error);
      });
  }

  // 編輯人員
  async function handleEditUser() {
    // let newGroupData = Object.fromEntries(Object.entries(formik.values).filter(([key]) => !key.includes('group_type')));
    await setPopUpMessage('編輯人員中');
    let roleToAdd = formik.values.role.filter(i => !oriAdminRoles.includes(i));
    // console.log('roleToAdd', roleToAdd);
    let roleToRemove = oriAdminRoles.filter(i => !formik.values.role.includes(i));
    // console.log('roleToRemove', roleToRemove);
    if (roleToAdd.length > 0) {
      await Promise.all(
        roleToAdd.map(async (r) => {
          await axios.post("/api/role/put_setAdmin",
            { member_id: userId, role_name: system_roles_dic[r], group_id: formik.values.group_name.split('_')[0] },
            {
              headers: {
                Authorization: `Bearer ${session.tocken.loginUserToken}`
              }
            })
            .then((res) => {
              // console.log(res);
            })
            .catch((err) => {
              // console.log(err);
            })
        })
      )
    }
    if (roleToRemove.length > 0) {
      await Promise.all(
        roleToRemove.map(async (r) => {
          let role_id = '';
          if (r === '單位管理員') {
            role_id = userInfo.role.group_admin.id;
          }
          if (r === '專案管理員') {
            role_id = userInfo.is_project_admin.id;
          }
          if(r === '系統管理員'){
            role_id = userInfo.role.super_admin.id;
          }
          await axios.delete(`/api/role/delete_deleteAdmin/${role_id}`,
            {
              headers: {
                Authorization: `Bearer ${session.tocken.loginUserToken}`
              }
            })
            .then((res) => {
              // console.log(res);
            })
            .catch((err) => {
              // console.log(err);
            })
        })
      )
    }

    let newUserData = formik.values;
    // console.log('newUserData', newUserData);
    let admin_roles_copy = newUserData.role;
    newUserData['username'] = newUserData['username'].trim();
    newUserData['email'] = newUserData['email'].trim();
    newUserData['useraccount'] = newUserData['useraccount'].trim();
    newUserData['group_id'] = newUserData.group_name.split('_')[0];
    // delete newUserData.role; // 這裡的role是admin roles
    // delete newUserData.group_name;
    await axios.put(`/api/user/edit/${userId}`,
      newUserData,
      {
        headers: {
          Authorization: `Bearer ${session.tocken.loginUserToken}`
        }
      })
      .then(async () => {
        await setPopUpMessage('編輯人員完成');
        await updateData(newUserData, admin_roles_copy);
        await onUpdate();
        await onCancel();
      })
      .catch(async (error) => {
        // console.log('edit user error');
        await setPopUpMessage('編輯人員失敗');
        // console.log('error', error);
      })
  }

  const handleAdminRoles = (event) => {
    const {
      target: { value },
    } = event;
    setFieldValue('role', typeof value === 'string' ? value.split(',') : value,)
  };

  const handleRenderSelectedAdminRolse = (s) => {
    // console.log('s', s);
    if (s.startsWith(',')) {
      return s.slice(1,);
    } else {
      return s;
    }
  }

  return (
    <>
      <FormikProvider value={formik}>
        <LocalizationProvider dateAdapter={AdapterDateFns}>
          <Form autoComplete="off" noValidate onSubmit={handleSubmit}>
            <DialogTitle>{user ? '編輯人員' : '新增人員'}</DialogTitle>
            <Divider />
            <DialogContent sx={{ p: 2.5 }}>
              <Grid container spacing={3}>
                <Grid item xs={12} md={8}>
                  <Grid container spacing={3}>

                    {/*填入單位資訊*/}
                    <Grid item xs={12}>
                      <Stack spacing={1.25}>
                        <InputLabel htmlFor="group-name">*單位</InputLabel>
                        <Select
                          value={values.group_name}
                          displayEmpty
                          name="select user group"
                          renderValue={(selected) => {
                            if (selected) {
                              if (selected.includes('_')) {
                                return selected.split('_')[2];
                              }
                              return selected;
                            }
                            return null;
                          }}
                          fullWidth
                          onChange={(selected) => {
                            setFieldValue('group_name', selected.target.value);
                          }}
                        >
                          {allGroups?.map((g) => {
                            // value=`${group_id}_${group_type}_${group_name}`
                            return <MenuItem value={`${g.id}_${g.group_type}_${g.group_name}`}>{g.group_name}</MenuItem>
                          })}
                        </Select>
                      </Stack>
                    </Grid>

                    {/*填入帳號資訊*/}
                    <Grid item xs={12}>
                      <Stack spacing={1.25}>
                        <InputLabel htmlFor="user-account">*帳號</InputLabel>
                        <TextField
                          fullWidth
                          id="user-account"
                          disabled={!!user}
                          placeholder=""
                          {...getFieldProps('useraccount')}
                          label={(checkUseraccount(values.useraccount) && '不可包含中文字元及"_"以外之特殊字元')}
                          error={checkUseraccount(values.useraccount)}
                          // error={Boolean(touched.useraccount && errors.useraccount)}
                          helperText={touched.useraccount && errors.useraccount}
                        />
                      </Stack>
                    </Grid>

                    {/*填入姓名資訊*/}
                    <Grid item xs={12}>
                      <Stack spacing={1.25}>
                        <InputLabel htmlFor="user-name">*姓名</InputLabel>
                        <TextField
                          fullWidth
                          id="user-name"
                          placeholder=""
                          {...getFieldProps('username')}
                          label={checkUsername(values.username) && '不可包含特殊字元'}
                          error={checkUsername(values.username)}
                          // error={Boolean(touched.username && errors.username)}
                          helperText={touched.username && errors.username}
                        />
                      </Stack>
                    </Grid>

                    {/*填入電子信箱*/}
                    <Grid item xs={12}>
                      <Stack spacing={1.25}>
                        <InputLabel htmlFor="user-email">E-mail</InputLabel>
                        <TextField
                          fullWidth
                          id="user-email"
                          placeholder=""
                          {...getFieldProps('email')}
                          // label={values.email?values.email:'123'}
                          label={(!checkEmail(values.email)) && checkEmailMsg(values.email)}
                          error={!checkEmail(values.email)}
                          helperText={touched.email && errors.email}
                        />
                      </Stack>
                    </Grid>

                    {/*填入角色資訊 ???複選嗎 api沒有role*/}
                    {user && (
                      <Grid item xs={12}>
                        <Stack spacing={1.25}>
                          <InputLabel htmlFor="role">角色</InputLabel>
                          <Select
                            value={values.role}
                            displayEmpty
                            multiple
                            name="select user admin roles"
                            renderValue={(selected) => {
                              if (selected) {
                                // console.log('selected.join(\', \')', selected.join(', '), selected);
                                return handleRenderSelectedAdminRolse(selected.join(', '));
                              }
                              return null;
                            }}
                            fullWidth
                            onChange={handleAdminRoles}
                          // onChange={(selected) => {
                          //     console.log('selected', selected);
                          //     setFieldValue('role', selected.target.value);
                          // }}
                          >
                            {system_roles.map((ri) => {
                              // console.log("user admin roles", userAdminRoles);
                              if(ri === '系統管理員' && !userPermission.includes('super_admin')) return null                                                     
                              return (
                                <MenuItem
                                  value={ri}
                                >
                                  <Checkbox checked={values.role.includes(ri)} />
                                  {ri}
                                </MenuItem>)
                            })}
                          </Select>
                        </Stack>
                      </Grid>
                    )}

                    {/* <Dialog open={popUp} onClose={onCancel}>
                      <DialogTitle>{popUpMessage}</DialogTitle>
                      {newUserPopup && (
                        <Button variant="contained" sx={{ bgcolor: "#226cea", minWidth: '100px' }} onClick={() => {
                          setNewUserPopup(false);
                          onCancel();
                        }} >
                          確定
                        </Button>
                      )}
                    </Dialog> */}

                    {(popUp && newUserPopup) ?
                      <StateControlDialog stateArrayOpenControl={[popUp, setPopUp]}
                        dialogTitle={popUpMessage} dialogContent={null}
                        disagreeButtonText={null} agreeButtonText="確定"
                        agreeButtonOnClick={() => {
                          setNewUserPopup(false);
                          onCancel();
                        }} /> : <></>}

                  </Grid>
                </Grid>
              </Grid>
            </DialogContent>
            <Divider />
            <DialogActions sx={{ p: 2.5 }}>
              <Grid container justifyContent="space-between" alignItems="center">
                <Grid item>
                  <Stack direction="row" spacing={2} alignItems="center">
                    <Button sx={{ minWidth: '100px' }} variant="outlined" onClick={onCancel}>
                      取消
                    </Button>
                    <Button type="submit" variant="contained" disabled={isSubmitting} sx={{ bgcolor: "#226cea", minWidth: '100px' }} >
                      確定
                    </Button>
                  </Stack>
                </Grid>
              </Grid>
            </DialogActions>
          </Form>
        </LocalizationProvider>
        <Dialog open={checkPopUp} onClose={() => { setCheckPopUp(false) }}>
          <DialogTitle>
            {popUpMessage}
          </DialogTitle>
        </Dialog>
      </FormikProvider>
      {/*{!isCreating && <AlertCustomerDelete title={user.fatherName} open={openAlert} handleClose={handleAlertClose} />}*/}
    </>
  );
};

AddUser.propTypes = {
  user: PropTypes.object,
  userId: PropTypes.number,
  allUsers: PropTypes.object,
  setAllUsers: PropTypes.func,
  onCancel: PropTypes.func
};

export default AddUser;
