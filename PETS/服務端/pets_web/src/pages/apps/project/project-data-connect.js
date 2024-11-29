// for single dataset

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
  useMediaQuery,
  List,
  ListItem,
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
import StateControlDialog from 'sections/apps/Dialog/state-dialog';
import { ConfigContext } from '../../../contexts/ConfigContext';


const ProjectDataConnect = () => {
  const theme = useTheme();
  const { data: session } = useSession();
  const router = useRouter();
  const user = useUser();
  const { allGroups, setAllGroups, projectGroup, setProjectGroup, status, setStatus, single, setSingle } = useContext(ConfigContext);
  const { project_name, project_id, project_status, isSingleDataset } = router.query;

  const [dataJoinMethod, setDataJoinMethod] = useState('Inner join');
  const [dataConnectSettings, setDataConnectSettings] = useState([{ left_datasetname: '', left_col: '', right_datasetname: '', right_col: '' }]);
  const [columnSettingCount, setColumnSettingCount] = useState(2);
  const [columnSettingContent, setColumnSettingContent] = useState(<></>);
  const [checkPopUp, setCheckPopUp] = useState(false);
  const [popUpMsg, setPopUpMsg] = useState(null);
  const [wroteLog, setWroteLog] = useState({});

  const fileNameRules = [
    '資料集格式說明 :',
    '資料集僅接受CSV檔案格式',
    '檔案與欄位資料名稱,僅可使用英數字與半形底線,上述三種元素之結合,不可中文、空白、全形字體。如 sample_2024.csv',
    '資料集需選擇資料來源單位(下拉選單),系統會透過來源單位的前綴字元,判斷是否符合專案內容設定。',
    '請確認新增專案時,有加入該資料集之來源單位與協作人員。',
    '最終資料集組合為來源單位的前綴字元+"_"+資料集名稱.csv。'
  ];
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

  // API: set new project status
  const handleSetProjectStatus = async (session, project_id, newStatus) => {
    const payload = {
      project_id: project_id,
      status: newStatus
    };
    const config = {
      headers: {
        Authorization: `Bearer ${session.tocken.loginUserToken}`
      }
    };
    const promiseResult = await axiosPlus({
      method: 'PUT',
      stateArray: null,
      url: '/api/project/put_projectStatus',
      payload: payload,
      config: config,
      showSuccessMsg: false
    });

    if (promiseResult.status == 200 && promiseResult.data.status == true) {
      console.log('PUT projectStatus success');
    } else console.log('PUT projectStatus fail', promiseResult);
  };

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

      let promiseResult;
      try {
        promiseResult = await axios.post(url, payload, config);
      }
      catch (error) {
        promiseResult = error.response;
      }
      // const promiseResult = await axiosPlus({ method: "POST", stateArray: null, url: url, payload: payload, config: config, showSuccessMsg: false, showErrorMsg: true });
      console.log("API /projects/insert response/error:\n", promiseResult);
      if (promiseResult.status === 400) {
        await setPopUpMsg(promiseResult.data.msg);
        await setCheckPopUp(true);
      }

      if (!wroteLog["createProject"]) {
        await petsLog(session, 0, `Login User ${user.account}建立新專案`, project_name);
        setWroteLog(prev => ({ ...prev, ["createProject"]: true }))
      }
      if (promiseResult.status === 200) {
        // Go back to projects-table
        await router.push('/apps/project/projects-table');
      }
    }
  }

  const handleSingleSave = async () => {
    // Fetch API /projects/singleinsert
    let { project_name, project_eng, enc_key, group_id, project_id } = router.query;
    // let checker = arr => arr.every(v => v === true);
    // const goSave = await handleCheck();
    // console.log('goSave', goSave, checker(goSave));


    if (dataConnectSettings[0].left_datasetname) {
      console.log('save project');
      let projectInsertPayload = {
        'project_name': project_name,
        "single_dataset": dataConnectSettings[0].left_datasetname,
        // 'join_func': dataConnectSettings,
      }

      const url = "/api/project/post_singleinsert";
      const payload = projectInsertPayload; // [TODO] need to fill in dynamic data
      console.log('payload', payload);
      const config = {
        headers: {
          Authorization: `Bearer ${session.tocken.loginUserToken}`
        },
      };

      let promiseResult;
      try {
        promiseResult = await axios.post(url, payload, config);
        console.log('promiseResult', promiseResult);
      }
      catch (error) {
        promiseResult = error.response;
        console.log(promiseResult)
      }
      // const promiseResult = await axiosPlus({ method: "POST", stateArray: null, url: url, payload: payload, config: config, showSuccessMsg: false, showErrorMsg: true });
      // console.log("API /projects/singleinsert response/error:\n", promiseResult);
      // if (promiseResult.status === 400) {
      //   await setPopUpMsg(promiseResult.data.msg);
      //   await setCheckPopUp(true);
      // }

      // if (!wroteLog["createProject"]) {
      //   await petsLog(session, 0, `Login User ${user.account}建立新專案`, project_name);
      //   setWroteLog(prev => ({ ...prev, ["createProject"]: true }))
      // }
      if (promiseResult.status === 200) {
        // Go back to projects-table
        handleSetProjectStatus(session, project_id, 1)
        await router.push('/apps/project/projects-table');
      }
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
        <Grid container sx={{ margin: "20px 0 0 50px" }}>
          <Grid item xs={2} />
          <Grid item xs={9}>
            <Stack direction='row'>
              <ConnectSetting dataConnections={dataConnectSettingsTemp} setDataConnections={setDataConnectSettings} index={i} />
              <IconButton>
                <RemoveCircleOutlineIcon sx={{ 'position': "relative", 'top': "-1px" }} onClick={() => handleDelete(i)} />
              </IconButton>
            </Stack>
          </Grid>
        </Grid>
      )
    }
    setColumnSettingContent(content);
    return content;
  };

  // API : fetch project member group (/api/projects/membergroupid)
  const handleFetchProjectMemberGroup = async (session, project_id, setProjectGroup) => {
    const config = {
      headers: {
        Authorization: `Bearer ${session.tocken.loginUserToken}`
      },
      params: {
        project_id: project_id
      }
    };
    const promiseResult = await axiosPlus({
      method: 'GET',
      stateArray: null,
      url: '/api/project/get_membergroupid',
      config: config,
      showSuccessMsg: false
    });

    if (promiseResult && promiseResult?.status == 200) {
      setProjectGroup(promiseResult.data.obj)
    } else {
      console.log("Error", promiseResult)
    }
  };

  useEffect(() => {
    // console.log('render cs', dataConnectSettings);
    renderColumnSettingContent({ columnSettingCount, dataConnectSettings })
    handleFetchProjectMemberGroup(session, project_id, setProjectGroup)

    setSingle(parseInt(isSingleDataset));
    setStatus(parseInt(project_status))

  }, [columnSettingCount, dataConnectSettings, single, status])


  return (
    <Page title="new project data connect">
      {/*<MainCard content={false}>*/}
      <Box sx={{ width: '750px', margin: "40px auto 60px auto" }} >
        <Box sx={{ width: "100%", alignItems: "center" }} >
          <ProjectStepper currentStep={0} terminatedStep={null} />
        </Box>
      </Box>

      <Box sx={{ width: {xs:'95%',xl:'100%'}, mb: "20px", mt: "50px" }}>
        <Grid container spacing={6} sx={{ ml: "50px", maxWidth: "1200px", }}>
          <Grid item>
            <Typography variant='h3' sx={{ marginBottom: "20px" }}>
              建立專案及設定
            </Typography>
          </Grid>

          <Grid container sx={{ margin: "20px 0 0 50px" }}>
            <Grid item xs={2}>
              <InputLabel>*專案名稱</InputLabel>
            </Grid>
            <Grid item xs={8}>
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

          <Grid container sx={{ margin: "20px 0 0 50px" }}>
            <Grid item xs={2}>
              <InputLabel>*資料鏈結欄位屬性設定</InputLabel>
            </Grid>
            <Grid item xs={9}>
              <List sx={{ marginBottom: "20px", marginLeft: "5px" }}>
                {fileNameRules.map((rule, index) => (
                  <ListItem key={index} sx={{ margin: 0, padding: 0 }}>
                    {index>0 && <Typography variant="caption">{index}. &nbsp;</Typography>}
                    <Typography variant="caption">{rule}</Typography>
                  </ListItem>
                ))}
              </List>
              <Stack direction='row'>
                <ConnectSetting dataConnections={dataConnectSettings} setDataConnections={setDataConnectSettings} index={0} />
              </Stack>
            </Grid>
          </Grid>
          {/*<Divider />*/}
          {/*{renderColumnSettingContent({ columnSettingCount, dataConnectSettings })}*/}
          {/* {columnSettingContent} */}
        </Grid>
        <Grid container row sx={{ marginTop: "20px", marginLeft: "15px" }}>
          <Grid container spacing={6} columns={15}>
            <Grid item xs={11} />
            <Grid item xs={4} xl={3} sx={{ display: "flex", flexDirection: "column", alignItems: "flex-start", justifyContent: "flex-end" }}>
              <Button
                variant="contained"
                onClick={handleSingleSave}
                sx={{ marginTop: "20px", px: "50px" }}
              >儲存設定
              </Button>
            </Grid>
          </Grid>

        </Grid>
      </Box>

      {(checkPopUp) && (
        <StateControlDialog stateArrayOpenControl={[checkPopUp, setCheckPopUp]}
          dialogTitle={null}
          dialogContent={popUpMsg}
          disagreeButtonText={null}
          agreeButtonText="確定"
          agreeButtonOnClick={() => { setCheckPopUp(false); }}
        />)}
      {/*</MainCard>*/}
    </Page>
  );
};

ProjectDataConnect.getLayout = function getLayout(page) {
  return <Layout>{page}</Layout>;
};

export default ProjectDataConnect;
