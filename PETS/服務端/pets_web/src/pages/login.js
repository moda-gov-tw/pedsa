import { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import axios from 'axios';
import GppBadIcon from '@mui/icons-material/GppBad';
import VerifiedUserOutlinedIcon from '@mui/icons-material/VerifiedUserOutlined';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';

// next
import { getProviders, getCsrfToken } from 'next-auth/react';

// material-ui
import {
  Grid,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  IconButton,
  Stack,
  Typography,
} from '@mui/material';
import CircularProgress from '@mui/material/CircularProgress';

// project import
import Layout from 'layout';
import Page from 'components/Page';
import AuthWrapper from 'sections/auth/AuthWrapper';
import AuthLogin from 'sections/auth/auth-forms/AuthLogin';


/**
 * Function: SignIn(登入畫面)
 *
 * @param {{ providers: object, csrfToken: string }} props
 *
 * @returns {JSX.Element}
 */
export default function SignIn({ providers, csrfToken }) {

  const [popUp, setPopUp] = useState(false);
  const [containerStatus, setContainerStatus] = useState(true);
  const [fileStatus, setFileStatus] = useState(true);
  const [dbStatus, setDbStatus] = useState(true);
  const [isLoading, setIsLoading] = useState(true);


  async function getHealthData() {
    await axios
      .get('/api/sys/get_containersStatus')
      .then(async (response) => {
        let containers_status = response.data.is_connection;
        setContainerStatus(containers_status);
      })
      .catch((error) => {
        // console.log('error', error);
        setContainerStatus(false);
      });
  }
  async function getFilePermissionData() {
    await axios
      .get('/api/sys/get_filePermission')
      .then(async (response) => {
        let file_status = response.data.is_match;
        setFileStatus(file_status);
        // setFileStatus(false)
      })
      .catch((error) => {
        // console.log('error', error);
        setFileStatus(false);
      });
  }
  async function getCheckDb() {
    await axios
      .get('/api/sys/get_checkDb')
      .then(async (response) => {
        let db_status = response.data.is_ready;
        setDbStatus(db_status);
      })
      .catch((error) => {
        // console.log('error', error);
        setDbStatus(false);
      });
  }

  const handleCheckSystemStatus = async () => {
    await setPopUp(true);
  };

  useEffect(()=>{
    async function fetchData() {
      await getHealthData();
      await getFilePermissionData();
      await getCheckDb();
      setIsLoading(false);
    }
  
    fetchData();
  },[popUp])

  // console.log('providers', providers);
  return (
    <Page title="Login">
      <AuthWrapper>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Stack direction="row" justifyContent="space-between" alignItems="baseline" sx={{ mb: { xs: -0.5, sm: 0.5 } }}>
              <Typography variant="h3" display="block">LOGO</Typography>
              <IconButton color="primary" onClick={handleCheckSystemStatus}>
                {isLoading ? (
                  <CircularProgress size={24} />
                ): containerStatus === false || fileStatus === false || dbStatus === false ? (
                   <GppBadIcon style={{color:'red'}} /> 
                ):(
                  <VerifiedUserOutlinedIcon/>
                )}
              </IconButton>
            </Stack>
          </Grid>
          <Grid item xs={12}>
            <AuthLogin providers={providers} csrfToken={csrfToken} />
          </Grid>
        </Grid>
        <Dialog
          open={popUp}
          onClose={() => setPopUp(false)}
          sx={{
            '& .MuiDialog-paper': {
              padding: '15px',
            },
          }}
        >
          <DialogTitle>
            <Typography variant="h6" sx={{ fontSize: '1.3rem', fontWeight:'bold' }}>
              系統狀態檢測
            </Typography>
          </DialogTitle>
          <DialogContent>
            <DialogContentText id="alert-dialog-description" sx={{ mb:1 }}>
              {containerStatus ? (
                <Stack direction="row" alignItems="center">
                  <CheckCircleIcon color="success" />
                  <Typography sx={{ ml: 2, fontSize: '1.02rem' }}>系統容器連線檢測通過</Typography>
                </Stack>
              ) : (
                <Stack direction="row" alignItems="center">
                  <CancelIcon color="error" />
                  <Typography sx={{ ml: 2, fontSize: '1.02rem' }}>系統容器連線檢測失敗</Typography>
                </Stack>
              )}
            </DialogContentText>
            <DialogContentText id="alert-dialog-description" sx={{ mb:1 }}>
              {fileStatus ? (
                <Stack direction="row" alignItems="center">
                  <CheckCircleIcon color="success" />
                  <Typography sx={{ ml: 2, fontSize: '1.02rem' }}>系統資料夾權限檢測通過</Typography>
                </Stack>
              ) : (
                <Stack direction="row" alignItems="center">
                  <CancelIcon color="error" />
                  <Typography sx={{ ml: 2, fontSize: '1.02rem' }}>系統資料夾權限檢測失敗</Typography>
                </Stack>
              )}
            </DialogContentText>
            <DialogContentText id="alert-dialog-description" sx={{ mb:1 }}>
              {dbStatus ? (
                <Stack direction="row" alignItems="center">
                  <CheckCircleIcon color="success" />
                  <Typography sx={{ ml: 2, fontSize: '1.02rem' }}>系統資料庫檢測通過</Typography>
                </Stack>
              ) : (
                <Stack direction="row" alignItems="center">
                  <CancelIcon color="error" />
                  <Typography sx={{ ml: 2, fontSize: '1.02rem' }}>系統資料庫檢測失敗</Typography>
                </Stack>
              )}
            </DialogContentText>
          </DialogContent>
          <DialogActions>
            <Button
              variant="contained"
              onClick={() => setPopUp(false)} 
              autoFocus
            >
              確定
            </Button>
          </DialogActions>
        </Dialog>
      </AuthWrapper>
    </Page>
  );
}

SignIn.propTypes = {
  providers: PropTypes.object,
  csrfToken: PropTypes.string
};

SignIn.getLayout = function getLayout(page) {
  return <Layout variant="auth">{page}</Layout>;
};

export async function getServerSideProps(context) {
  const providers = await getProviders();
  const csrfToken = await getCsrfToken(context);

  return {
    props: { providers, csrfToken }
  };
}
