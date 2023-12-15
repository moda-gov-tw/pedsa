import PropTypes from 'prop-types';
import React from 'react';

// next
import Image from 'next/image';
import NextLink from 'next/link';
import { useSession, getSession, signIn } from 'next-auth/react';

// material-ui
import {
  Box,
  useMediaQuery,
  Button,
  Checkbox,
  Divider,
  FormControlLabel,
  FormHelperText,
  Grid,
  Link,
  InputAdornment,
  InputLabel,
  OutlinedInput,
  Stack,
  Typography
} from '@mui/material';

// third party
import * as Yup from 'yup';
import { Formik } from 'formik';

// project import
import FirebaseSocial from './FirebaseSocial';
import { DEFAULT_PATH } from 'config';
import IconButton from 'components/@extended/IconButton';
import AnimateButton from 'components/@extended/AnimateButton';
import petsLog from 'sections/apps/logger/insert-system-log';

// assets
import { EyeOutlined, EyeInvisibleOutlined } from '@ant-design/icons';

const Auth0 = '/assets/images/icons/auth0.svg';
const Cognito = '/assets/images/icons/aws-cognito.svg';
const Google = '/assets/images/icons/google.svg';

// ============================|| AWS CONNITO - LOGIN ||============================ //
/**
 * Function : AuthLogin(登入資訊輸入框)
 *
 * Child component of `SignIn`
 *
 * @param {{ providers: object, csrfToken: string }}
 *
 * @returns {JSX.Element}
*/
const AuthLogin = ({ providers, csrfToken }) => {
  // const matchDownSM = useMediaQuery((theme) => theme.breakpoints.down('sm'));
  const [checked, setChecked] = React.useState(false);
  const [capsWarning, setCapsWarning] = React.useState(false);

  const { data: session } = useSession();

  const [showPassword, setShowPassword] = React.useState(false);
  const handleClickShowPassword = () => {
    setShowPassword(!showPassword);
  };

  const handleMouseDownPassword = (event) => {
    event.preventDefault();
  };

  const onKeyDown = (keyEvent) => {
    if (keyEvent.getModifierState('CapsLock')) {
      setCapsWarning(true);
    } else {
      setCapsWarning(false);
    }
  };

  const recordLogin = (session) => {
    const currentDate = new Date();
    petsLog(session, 0, `${session.tocken.account}帳號 登入，登入時間: ${currentDate}`);
  }

  return (
    <>
      <Formik
        initialValues={{
          account: '',
          password: '',
          submit: null
        }}
        validationSchema={Yup.object().shape({
          account: Yup.string(),
          password: Yup.string().max(255)
        })}
        onSubmit={(values, { setErrors, setSubmitting }) => {
          signIn('login', {
            redirect: false,
            account: values.account,
            password: values.password,
            callbackUrl: DEFAULT_PATH
          }).then((res) => {
            // signIn will then return a Promise, 
            // -> const {error: string | undefined, status: number, ok: boolean, url: string | null} = res = Promise;
            if (res?.error) {
              // Sign-in fail
              setErrors({ submit: res.error });
              setSubmitting(false);
            } else {
              // Sign-in success
              getSession().then((latestSession) => {
                // getSession() is a client side only api` to return the current active session.
                // -> it will send a request to /api/auth/session and returns a promise with a session object, or null if no session exists.
                if (latestSession)
                  recordLogin(latestSession);
              });
              setSubmitting(false);
            }
          });
        }}
      >
        {({ errors, handleBlur, handleChange, handleSubmit, isSubmitting, touched, values }) => (
          <form noValidate onSubmit={handleSubmit}>
            <input name="csrfToken" type="hidden" defaultValue={csrfToken} />
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Stack spacing={1}>
                  <InputLabel htmlFor="account-login">帳號</InputLabel>
                  <OutlinedInput
                    id="account-login"
                    type="account"
                    value={values.account}
                    name="account"
                    onBlur={handleBlur}
                    onChange={handleChange}
                    placeholder="帳號"
                    fullWidth
                    error={Boolean(touched.account && errors.account)}
                  />
                  {touched.account && errors.account && (
                    <FormHelperText error id="standard-weight-helper-text-email-login">
                      {errors.account}
                    </FormHelperText>
                  )}
                </Stack>
              </Grid>
              <Grid item xs={12}>
                <Stack spacing={1}>
                  <InputLabel htmlFor="password-login">密碼</InputLabel>
                  <OutlinedInput
                    fullWidth
                    color={capsWarning ? 'warning' : 'primary'}
                    error={Boolean(touched.password && errors.password)}
                    id="-password-login"
                    type={showPassword ? 'text' : 'password'}
                    value={values.password}
                    name="password"
                    onBlur={(event) => {
                      setCapsWarning(false);
                      handleBlur(event);
                    }}
                    onKeyDown={onKeyDown}
                    onChange={handleChange}
                    endAdornment={
                      <InputAdornment position="end">
                        <IconButton
                          aria-label="toggle password visibility"
                          onClick={handleClickShowPassword}
                          onMouseDown={handleMouseDownPassword}
                          edge="end"
                          color="secondary"
                        >
                          {showPassword ? <EyeOutlined /> : <EyeInvisibleOutlined />}
                        </IconButton>
                      </InputAdornment>
                    }
                    placeholder="密碼"
                  />
                  {capsWarning && (
                    <Typography variant="caption" sx={{ color: 'warning.main' }} id="warning-helper-text-password-login">
                      Caps lock on!
                    </Typography>
                  )}
                  {touched.password && errors.password && (
                    <FormHelperText error id="standard-weight-helper-text-password-login">
                      {errors.password}
                    </FormHelperText>
                  )}
                </Stack>
              </Grid>

              {/*<Grid item xs={12} sx={{ mt: -1 }}>*/}
              {/*  <Stack direction="row" justifyContent="space-between" alignItems="center" spacing={2}>*/}
              {/*    <FormControlLabel*/}
              {/*      control={*/}
              {/*        <Checkbox*/}
              {/*          checked={checked}*/}
              {/*          onChange={(event) => setChecked(event.target.checked)}*/}
              {/*          name="checked"*/}
              {/*          color="primary"*/}
              {/*          size="small"*/}
              {/*        />*/}
              {/*      }*/}
              {/*      label={<Typography variant="h6">記住我</Typography>}*/}
              {/*    />*/}
              {/*    <NextLink href={session ? '/auth/forgot-password' : '/forgot-password'} passHref>*/}
              {/*      <Link variant="h6" color="text.primary">*/}
              {/*        忘記密碼?*/}
              {/*      </Link>*/}
              {/*    </NextLink>*/}
              {/*  </Stack>*/}
              {/*</Grid>*/}
              {errors.submit && (
                <Grid item xs={12}>
                  <FormHelperText error>{errors.submit}</FormHelperText>
                </Grid>
              )}
              <Grid item xs={12}>
                <AnimateButton>
                  <Button disableElevation disabled={isSubmitting} fullWidth size="large" type="submit" variant="contained" color="primary">
                    登入
                  </Button>
                </AnimateButton>
              </Grid>
            </Grid>
          </form>
        )}
      </Formik>

      {!providers && (
        <Box sx={{ mt: 3 }}>
          <FirebaseSocial />
        </Box>
      )}
    </>
  );
};

AuthLogin.propTypes = {
  providers: PropTypes.object,
  csrfToken: PropTypes.string
};

export default AuthLogin;
