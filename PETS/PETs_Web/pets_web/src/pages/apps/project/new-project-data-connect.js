import PropTypes from 'prop-types';
import { useContext, useEffect, useMemo, useState } from 'react';
import * as React from 'react';
import axiosPlus from 'sections/api/axiosPlus';

// next
import { useSession, } from 'next-auth/react';
import { useRouter } from 'next/router';

// material-ui
import { styled } from '@mui/material/styles';
import Paper from '@mui/material/Paper';
import { useTheme } from '@mui/material/styles';
import {
  Box,
  Button, Dialog, DialogTitle,
  Divider,
  Grid,
  IconButton,
  InputLabel,
  Menu,
  MenuItem,
  Select,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Tooltip,
  Typography,
  useMediaQuery
} from '@mui/material';
import ClearIcon from '@mui/icons-material/Clear';
import AddIcon from '@mui/icons-material/Add';


// third-party
import axios from 'axios';
import { useFilters, useExpanded, useGlobalFilter, useRowSelect, useSortBy, useTable, usePagination } from 'react-table';

// project import
import { join_method_dic } from 'data/join-method';
import Layout from 'layout';
import ConnectSetting from 'sections/apps/data-connect/connect-setting';
import Page from 'components/Page';
import MainCard from 'components/MainCard';
import ScrollX from 'components/ScrollX';
import {
  HeaderSort,
  IndeterminateCheckbox,
  TableRowSelection
} from 'components/third-party/ReactTable';
import BasicAutocomplete from '../../../sections/components-overview/autocomplete/BasicAutocomplete';
import { renderFilterTypes, GlobalFilter } from 'utils/react-table';
import ProjectStepper from 'sections/apps/progress/project_stepper';
import { mockProjectMembers } from '../../../utils/mock-project-members';
import { projectInsertPayload } from '../../../utils/mock-project-insert-example';
import RemoveCircleOutlineIcon from "@mui/icons-material/RemoveCircleOutline";
import useUser from "hooks/useUser";
import petsLog from "sections/apps/logger/insert-system-log";

const NewProjectDataConnect = () => {
  const theme = useTheme();
  const { data: session } = useSession();
  const router = useRouter();
  const user = useUser();

  const [dataJoinMethod, setDataJoinMethod] = useState('Inner join');
  const [dataConnectSettings, setDataConnectSettings] = useState([{ left_datasetname: '', left_col: '', right_datasetname: '', right_col: '' }]);
  const [columnSettingCount, setColumnSettingCount] = useState(2);
  const [columnSettingContent, setColumnSettingContent] = useState(<></>);
  const [checkPopUp, setCheckPopUp] = useState(false);
  const [popUpMsg, setPopUpMsg] = useState(null);
  const [wroteLog, setWroteLog] = useState({});

  // console.log('dataConnectSettings', dataConnectSettings);

  // useEffect(() => {
  //   const { project_name, project_eng, enc_key, group_id, project_role } = router.query;
  //   console.log(project_name, project_eng, enc_key);
  //   console.log('group_id', group_id);
  //   console.log('project_members', JSON.parse(project_role));
  //   // const { name, age } = router.query;
  //   // console.log(name, age);
  // }, []);

  // useEffect(() => {
  // getUserTasks();
  // }, []);

  const handleClose = () => {
    console.log('close');
  };

  const handleJoinMethodSelect = (event) => {
    setDataJoinMethod(event.target.value);
  };

  const handleCheck = async () => {
    let temp = [];
    await Promise.all(
      await dataConnectSettings.map(async (dc) => {
        console.log('dc', dc);
        if (dc['left_datasetname'] === '' || dc['left_col'] === '' || dc['right_datasetname'] === '' || dc['right_col'] === '') {
          await setPopUpMsg('資料鏈結不可以為空');
          await setCheckPopUp(true);
          await temp.push(false);
        } else {
          await temp.push(true);
        }
      })
    )
    return temp;
  }

  const handleSave = async () => {
    // Fetch API /projects/insert
    let { project_name, project_eng, enc_key, group_id, project_role } = router.query;
    let checker = arr => arr.every(v => v === true);
    const goSave = await handleCheck();
    console.log('goSave', goSave, checker(goSave));
    if (checker(goSave)) {
      console.log('save project');
      let projectInsertPayload = {
        'project_name': project_name, 'project_eng': project_eng, 'enc_key': enc_key, 'group_id': parseInt(group_id),
        'join_type': join_method_dic[dataJoinMethod], 'join_func': dataConnectSettings, 'project_role': JSON.parse(project_role),
        "aes_col": "",
        "jointablecount": 0,
        "jointablename": "",
      }
      const url = "/api/project/post_projectInsert";
      const payload = projectInsertPayload; // [TODO] need to fill in dynamic data
      console.log('payload', payload);
      const config = {
        headers: {
          Authorization: `Bearer ${session.tocken.loginUserToken}`
        },
      };
      const promiseResult = await axiosPlus({ method: "POST", stateArray: null, url: url, payload: payload, config: config, showSuccessMsg: false });
      console.log("API /projects/insert response:\n", promiseResult);
      if (!wroteLog["createProject"]) {
        await petsLog(session, 0, `Login User ${user.account}建立新專案${project_name}成功`, project_name);
        setWroteLog(prev => ({ ...prev, ["createProject"]: true }))
      }
      // Go back to projects-table
      router.push('/apps/project/projects-table');
    }
  }

  const handleDelete = async (index) => {
    await setColumnSettingCount(columnSettingCount - 1);
    const newDataConnections = [
      ...dataConnectSettings.slice(0, index),
      ...dataConnectSettings.slice(index + 1)
    ];
    await setDataConnectSettings(newDataConnections);
  }

  const renderColumnSettingContent = ({ columnSettingCount, dataConnectSettings }) => {
    // console.log('dataConnectSettings in columnSettingContent', dataConnectSettings);
    let dataConnectSettingsTemp = [...dataConnectSettings];
    let content = [];
    for (let i = 1; i < columnSettingCount; i++) {
      if (!dataConnectSettingsTemp[i]) {
        dataConnectSettingsTemp.push({ left_datasetname: '', left_col: '', right_datasetname: '', right_col: '' });
      }
      // console.log('dataConnectSettings after push', dataConnectSettingsTemp);

      content.push(
        <Grid container item spacing={3}>
          <Grid container spacing={12}>
            <Grid item lg={2} />
            <Grid item lg={8}>
              <Stack direction='row' spacing={2}>
                <ConnectSetting dataConnections={dataConnectSettingsTemp} setDataConnections={setDataConnectSettings} index={i} />
                <IconButton>
                  <RemoveCircleOutlineIcon sx={{ 'position': "relative", 'top': "-1px" }} onClick={() => handleDelete(i)} />
                </IconButton>
              </Stack>
            </Grid>
          </Grid>
        </Grid>
      )
    }
    setColumnSettingContent(content);
    return content;
  };

  useEffect(() => {
    // console.log('render cs', dataConnectSettings);
    renderColumnSettingContent({ columnSettingCount, dataConnectSettings })
  }, [columnSettingCount, dataConnectSettings])



  return (
    <Page title="Customer List">
      {/*<MainCard content={false}>*/}
      <Box sx={{ width: '750px',  margin:"20px auto 60px auto" }} >
        <Box sx={{ width: "100%", alignItems: "center" }} >
          <ProjectStepper currentStep={0} terminatedStep={null} />
        </Box>
      </Box>

      <Box sx={{ width: '100%', mb: "20px", mt: "50px" }}>
        <Grid container spacing={6} sx={{ ml: "50px" }}>
          <Grid container item>
            <Grid item>
              <Stack>
                <Typography variant='h3'>
                  建立專案及設定
                </Typography>
                <Divider />
              </Stack>
            </Grid>
          </Grid>

          <Grid container item spacing={3}>
            <Grid container spacing={12} >
              <Grid item lg={2}>
                <InputLabel sx={{ textAlign: { xs: 'left', sm: 'left', ml: "250px" } }}>專案名稱</InputLabel>
              </Grid>
              <Grid item lg={8}>
                <TextField
                  fullWidth
                  value={router.query.project_name}
                  InputProps={{ readOnly: true, disableUnderline: true }}
                  disabled
                  variant="filled"
                  sx={{
                    "& .MuiInputBase-input.Mui-disabled": {
                      backgroundColor: "disableBGColor",
                      WebkitTextFillColor: "#000000",
                      padding: "10px"
                    }
                  }}
                />
              </Grid>
            </Grid>
          </Grid>

          <Grid container item spacing={3}>
            <Grid container spacing={12}>
              <Grid item lg={2}>
                <Typography fullWidth multiline sx={{ textAlign: { xs: 'left', sm: 'left', ml: "250px" } }}>資料鏈結方式</Typography>
              </Grid>
              <Grid item lg={4}>
                <Select
                  fullWidth
                  value={dataJoinMethod}
                  displayEmpty
                  name="select data connect method"
                  renderValue={(selected) => {
                    return selected;
                  }}
                  onChange={handleJoinMethodSelect}
                >
                  <MenuItem value={'Full outer join'}>Full outer join</MenuItem>
                  <MenuItem value={'Inner join'}>Inner join</MenuItem>
                </Select>
              </Grid>
            </Grid>
          </Grid>

          <Grid container item spacing={3}>
            <Grid container spacing={12}>
              <Grid item lg={2}>
                <Typography multiline sx={{ textAlign: { xs: 'left', sm: 'left' } }}>資料鏈結欄位屬性設定</Typography>
              </Grid>

              <Grid item lg={8}>
                <Stack direction='row' spacing={2}>
                  <ConnectSetting dataConnections={dataConnectSettings} setDataConnections={setDataConnectSettings} index={0} />
                  <IconButton disabled>
                    <RemoveCircleOutlineIcon sx={{ 'position': "relative", 'top': "-1px" }} onClick={() => handleDelete(i)} />
                  </IconButton>
                </Stack>
              </Grid>
            </Grid>
          </Grid>
          {/*<Divider />*/}

          {/*{renderColumnSettingContent({ columnSettingCount, dataConnectSettings })}*/}

          {columnSettingContent}
        </Grid>
      </Box>
      <Box
        m={1}
        display="flex"
        justifyContent="flex-end"
        alignItems="flex-end"
      >
        <Button variant="outlined" onClick={() => { setColumnSettingCount(columnSettingCount + 1) }} startIcon={<AddIcon />} />
      </Box>
      <Box
        m={1}
        display="flex"
        justifyContent="flex-end"
        alignItems="flex-end"
      >
        <Stack direction='row' spacing={2} sx={{ 'mt': '10px' }}>
          <Button variant="contained" onClick={handleSave}>儲存設定</Button>
          {/*<Button variant="contained">資料匯入及鏈結設定檢查</Button>*/}
        </Stack>
      </Box>
      <Dialog open={checkPopUp} onClose={() => { setCheckPopUp(false) }}>
        <DialogTitle>
          {popUpMsg}
        </DialogTitle>
      </Dialog>
      {/*</MainCard>*/}
    </Page>
  );
};

NewProjectDataConnect.getLayout = function getLayout(page) {
  return <Layout>{page}</Layout>;
};

export default NewProjectDataConnect;
