import PropTypes from 'prop-types';
import { useEffect, useState } from 'react';
import * as React from 'react';

// next
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/router';
import { signOut } from 'next-auth/react';

// material-ui
import { useTheme } from '@mui/material/styles';
import {
  Button,
  Dialog,
  DialogTitle,
  Divider,
  Grid,
  IconButton,
  InputAdornment,
  InputLabel,
  OutlinedInput,
  Stack,
  TextField,
  Typography
} from '@mui/material';
import VisibilityOutlinedIcon from '@mui/icons-material/VisibilityOutlined';
import VisibilityOffOutlinedIcon from '@mui/icons-material/VisibilityOffOutlined';

// third-party
import axios from 'axios';

// project import
import useUser from 'hooks/useUser';
import Layout from 'layout';
import Page from 'components/Page';
import petsLog from 'sections/apps/logger/insert-system-log';
import StateControlDialog from 'sections/apps/Dialog/state-dialog';
import { containsTabOrSpace, containsFullWidthChars } from 'utils/check-rules';

// ==============================|| PASSWORD RESET ||============================== //

const PasswordReset = () => {
  const theme = useTheme();
  const { data: session } = useSession();
  const router = useRouter();
  const user = useUser();
  // const { allUsers, setAllUsers, allGroups, setAllGroups } = useContext(ConfigContext); // 所有單位、人員
  const [userInfo, setUserInfo] = useState(null);
  const [showPassword, setShowPassword] = useState({ 0: false, 1: false, 2: false });
  const [oriPassword, setOriPassword] = useState(null);
  const [newPassword1, setNewPassword1] = useState(null);
  const [newPassword2, setNewPassword2] = useState(null);
  const [popUp, setPopUp] = useState(false);
  const [popUpTitle, setPopUpTitle] = useState('');
  const [popUpMsg, setPopUpMsg] = useState(null);
  const [wroteLog, setWroteLog] = useState({});

  // 取得登入使用者資訊
  const getUserInfo = async (token) => {
    // console.log('getUserInfo');
    await axios
      .get(`/api/user/get_info/${user.id}`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      })
      .then((response) => {
        // console.log('get user info', response.data.obj);
        setUserInfo(response.data.obj);
      })
      .catch((error) => {
        // console.log('get user info error', error);
      });
  };

  useEffect(() => {
    // 取得登入使用者資訊
    getUserInfo(session.tocken.loginUserToken);
  }, []);

  function handlePasswordCheck1() {
    if (oriPassword && newPassword1 && oriPassword === newPassword1) {
      setPopUpTitle('修改密碼失敗');
      setPopUpMsg('新密碼不得與舊密碼相同');
      setPopUp(true);
      return false;
    }
    setPopUpMsg('');
    return true;
  }

  function handlePasswordCheck2() {
    if (!newPassword1) {
      setPopUpTitle('修改密碼失敗');
      setPopUpMsg('請輸入新密碼');
      setPopUp(true);
      return false;
    }
    if (newPassword1 !== newPassword2) {
      setPopUpTitle('修改密碼失敗');
      setPopUpMsg('新密碼不一致');
      setPopUp(true);
      return false;
    }
    setPopUpMsg('');
    return true;
  }

  function handlePasswordCheck3() {
    // 命名規則:
    if (containsTabOrSpace(newPassword1) || containsTabOrSpace(newPassword2) || containsFullWidthChars(newPassword1) || containsFullWidthChars(newPassword2)) {
      setPopUpTitle('修改密碼失敗');
      setPopUpMsg('密碼為英數混和的8~12個字元，至少包含一個大寫字母，且不可以包含tab鍵、空格以及全形字元');
      setPopUp(true);
      return false;
    }
    setPopUpMsg('');
    return true;
  }

  async function handleClick() {
    let set_password = await handlePasswordCheck1();
    if (set_password) {
      set_password = await handlePasswordCheck2();
    }
    if (set_password) {
      set_password = await handlePasswordCheck3();
    }
    if (set_password) {
      let payload = {
        password: oriPassword,
        new_password_1: newPassword1,
        new_password_2: newPassword2
      };
      const config = {
        headers: {
          Authorization: `Bearer ${session.tocken.loginUserToken}`
        }
      };
      await axios
        .put('/api/user/put_uppwd/', payload, config)
        .then(async () => {
          await setPopUpTitle('修改密碼成功');
          if (!wroteLog['resetPassword']) {
            await petsLog(session, 0, `Login User ${user.account}修改 ${user.account} 密碼成功`);
            setWroteLog((prev) => ({ ...prev, ['resetPassword']: true }));
          }
          await setPopUp(true);
        })
        .catch(async (error) => {
          await setPopUpTitle('修改密碼失敗');
          await setPopUpMsg('請確認舊密碼正確，且新密碼為英數混合的8~12個字元，至少包含一個大寫字母，可以包含特殊字元但不可以包含tab鍵以及空格');
          if (!wroteLog['resetPassword']) {
            await petsLog(session, 0, `Login User ${user.account}修改 ${user.account} 密碼失敗`);
            setWroteLog((prev) => ({ ...prev, ['resetPassword']: true }));
          }
          await setPopUp(true);
          // console.log('reset error', error);
        });
    }
  }

  async function handleResetSuccess() {
    await localStorage.clear();
    await signOut({ redirect: false });
  }

  const handleOriPassword = (event) => {
    setOriPassword(event.target.value);
  };

  const handleNewPassword1 = (event) => {
    setNewPassword1(event.target.value);
  };

  const handleNewPassword2 = (event) => {
    setNewPassword2(event.target.value);
  };

  const handleClickShowPassword = (password_id) => {
    const temp = { ...showPassword };
    temp[password_id] = !showPassword[password_id];
    setShowPassword(temp);
    // setShowPassword({...showPassword, password_id: !showPassword[password_id]})
  };

  return (
    <Page title="Password Reset">
      <Grid container spacing={6} sx={{ ml: '50px', maxWidth: '1200px' }}>
        <Grid item>
          <Typography variant="h3" sx={{ marginBottom: '20px' }}></Typography>
        </Grid>

        <Grid container sx={{ margin: '20px 0 0 50px' }}>
          <Grid item xs={2}>
            <InputLabel sx={{ width: '100%' }}>帳號</InputLabel>
          </Grid>
          <Grid item xs={8}>
            <TextField
              fullWidth
              value={userInfo ? userInfo.username : ''}
              InputProps={{ readOnly: true, disableUnderline: true }}
              disabled
              variant="filled"
              sx={{
                '& .MuiInputBase-root': {
                  border: {
                    borderWidth: '1px',
                    borderStyle: 'solid',
                    borderRadius: 4
                  },
                  '& .MuiInputBase-input.Mui-disabled': {
                    WebkitTextFillColor: '#000000',
                    backgroundColor: 'disableBGColor',
                    padding: '10px',
                    border: {
                      borderRadius: 3
                    }
                  }
                }
              }}
            />
          </Grid>
        </Grid>

        <Grid container sx={{ margin: '20px 0 0 50px' }}>
          <Grid item xs={2}>
            <InputLabel sx={{ width: '100%' }}>單位</InputLabel>
          </Grid>
          <Grid item xs={8}>
            <TextField
              fullWidth
              value={userInfo ? userInfo.group_name : ''}
              InputProps={{ readOnly: true, disableUnderline: true }}
              disabled
              variant="filled"
              sx={{
                '& .MuiInputBase-root': {
                  border: {
                    borderWidth: '1px',
                    borderStyle: 'solid',
                    borderRadius: 4
                  },
                  '& .MuiInputBase-input.Mui-disabled': {
                    WebkitTextFillColor: '#000000',
                    backgroundColor: 'disableBGColor',
                    padding: '10px',
                    border: {
                      borderRadius: 3
                    }
                  }
                }
              }}
            />
          </Grid>
        </Grid>

        <Grid container sx={{ margin: '20px 0 0 50px' }}>
          <Grid item xs={2}>
            <InputLabel sx={{ width: '100%' }}>密碼</InputLabel>
          </Grid>
          <Grid item xs={8}>
            <Grid item xs={2}>
              <InputLabel sx={{ textAlign: { xs: 'left', sm: 'left' } }}>舊密碼</InputLabel>
            </Grid>
            <Grid item xs={8} sx={{ marginBottom: '10px' }}>
              <OutlinedInput
                fullWidth
                type={showPassword[0] ? 'text' : 'password'}
                value={oriPassword}
                onChange={handleOriPassword}
                endAdornment={
                  <InputAdornment position="end">
                    <IconButton
                      aria-label="toggle password visibility"
                      onClick={() => {
                        handleClickShowPassword(0);
                      }}
                      edge="end"
                      color="secondary"
                    >
                      {showPassword[0] ? <VisibilityOutlinedIcon /> : <VisibilityOffOutlinedIcon />}
                    </IconButton>
                  </InputAdornment>
                }
              />
            </Grid>
            <Grid item xs={2}>
              <InputLabel sx={{ textAlign: { xs: 'left', sm: 'left' } }}>新密碼</InputLabel>
            </Grid>
            <Grid item xs={8} sx={{ marginBottom: '10px' }}>
              <OutlinedInput
                fullWidth
                type={showPassword[1] ? 'text' : 'password'}
                value={newPassword1}
                onChange={handleNewPassword1}
                endAdornment={
                  <InputAdornment position="end">
                    <IconButton
                      aria-label="toggle password visibility"
                      onClick={() => {
                        handleClickShowPassword(1);
                      }}
                      edge="end"
                      color="secondary"
                    >
                      {showPassword[1] ? <VisibilityOutlinedIcon /> : <VisibilityOffOutlinedIcon />}
                    </IconButton>
                  </InputAdornment>
                }
                placeholder={'密碼為英數混和的8~12個字元，至少包含一個大寫字母，且不可以包含tab鍵以及空格'}
              />
            </Grid>
            <Grid item xs={2}>
              <InputLabel sx={{ textAlign: { xs: 'left', sm: 'left' } }}>再次輸入密碼</InputLabel>
            </Grid>
            <Grid item xs={8} sx={{ marginBottom: '10px' }}>
              <OutlinedInput
                fullWidth
                type={showPassword[2] ? 'text' : 'password'}
                value={newPassword2}
                onChange={handleNewPassword2}
                endAdornment={
                  <InputAdornment position="end">
                    <IconButton
                      aria-label="toggle password visibility"
                      onClick={() => {
                        handleClickShowPassword(2);
                      }}
                      edge="end"
                      color="secondary"
                    >
                      {showPassword[2] ? <VisibilityOutlinedIcon /> : <VisibilityOffOutlinedIcon />}
                    </IconButton>
                  </InputAdornment>
                }
              />
            </Grid>
          </Grid>
        </Grid>

        <Grid container item>
          <Grid container spacing={6}>
            <Grid item xs={8} />
            <Grid item xs={2}>
              <Button variant="contained" fullWidth onClick={handleClick}>
                確定
              </Button>
            </Grid>
          </Grid>
        </Grid>
      </Grid>
      {popUp ? (
        <StateControlDialog
          stateArrayOpenControl={[popUp, setPopUp]}
          dialogTitle={popUpTitle}
          dialogContent={
            // (popUpTitle === '修改密碼成功') ? `${userInfo.email}帳號已開通` : ((popUpTitle === '修改密碼失敗') ? popUpMsg : "")
            popUpTitle === '修改密碼成功'
              ? userInfo.ischange
                ? ``
                : `${userInfo.email}帳號已開通`
              : popUpTitle === '修改密碼失敗'
                ? popUpMsg
                : ''
          }
          disagreeButtonText={null}
          agreeButtonText="確定"
          agreeButtonOnClick={() => {
            setPopUp(false);
            if (popUpTitle === '修改密碼成功') {
              router.push('/apps/project/projects-table');
            }
          }}
        />
      ) : (
        <></>
      )}
    </Page>
  );
};

PasswordReset.getLayout = function getLayout(page) {
  return <Layout>{page}</Layout>;
};

export default PasswordReset;
