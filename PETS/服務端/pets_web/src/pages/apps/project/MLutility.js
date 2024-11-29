import { useEffect, useMemo, useState } from 'react';
import * as React from 'react';
// next
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/router';

// material-ui
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Divider,
  Grid,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  TextField,
  Typography,
  Box
} from '@mui/material';

// third-party
import axios from 'axios';

// project import
import useUser from 'hooks/useUser';
import Layout from 'layout';
import Page from 'components/Page';
import MainCard from 'components/MainCard';
import ScrollX from 'components/ScrollX';
import ColumnCheckboxTable from 'sections/apps/ml-utility/column-checkbox-table';
import { MLUtilityDic } from 'data/utility-report';
import axiosPlus from '../../../sections/api/axiosPlus';
import petsLog from '../../../sections/apps/logger/insert-system-log';
import { sub_sys_name } from '../../../data/sub_system_name';
import StateControlDialog from 'sections/apps/Dialog/state-dialog';

// ==============================|| MLUtility ||============================== //

const MLUtility = () => {
  const { data: session } = useSession();
  const router = useRouter();
  const user = useUser();

  const [sampleDataInfo, setSampleDataInfo] = useState(null);
  const [sampleData, setSampleData] = useState(null);
  const [colData,setColData] = useState(null)
  const [subsystemOptions, setSubsystemOptions] = useState(null);
  const [selectedDataset, setSelectedDataset] = useState(null);
  const [columnsSelected, setColumnsSelected] = useState({}); // {'c1': true, 'c2': false}
  const [popUp, setPopUp] = useState(false);
  const [popUpMsg, setPopUpMsg] = useState(null);
  const [wroteLog, setWroteLog] = useState({});

  // 由專案狀態取得子系統資料集選項(K匿名強化資料集、合成強化資料集)
  async function getSubsystemDatasetOptions(project_id, project_name) {
    let subsystemOptions_temp = [];
    let k_url = '/api/project/get_k_checkstatus';
    let syn_url = '/api/project/get_syn_checkstatus';
    let dp_url = '/api/project/get_dp_checkstatus';
    const config = {
      headers: { Authorization: `Bearer ${session.tocken.loginUserToken}` },
      params: {
        project_id: project_id,
        project_name: project_name
      }
    };
    const k_promiseResult = await axiosPlus({
      method: 'GET',
      stateArray: null,
      url: k_url,
      config: config,
      showSuccessMsg: false
    });
    // console.log('k_promiseResult', k_promiseResult);
    if (k_promiseResult && k_promiseResult.data[0].obj.project_status >= 11) {
      await subsystemOptions_temp.push('K匿名強化資料集');
    }
    const syn_promiseResult = await axiosPlus({
      method: 'GET',
      stateArray: null,
      url: syn_url,
      config: config,
      showSuccessMsg: false
    });
    // console.log('syn_promiseResult', syn_promiseResult);
    if (syn_promiseResult && syn_promiseResult.data[0].obj.project_status >= 8) {
      await subsystemOptions_temp.push('合成強化資料集');
    }

    const dp_promiseResult = await axiosPlus({
      method: 'GET',
      stateArray: null,
      url: dp_url,
      config: config,
      showSuccessMsg: false
    });
    if (dp_promiseResult && dp_promiseResult.data[0].obj.project_status >= 7) {
      await subsystemOptions_temp.push('差分強化資料集');
    }

    setSubsystemOptions(subsystemOptions_temp);
  }

  // 取得專案sample data、資料集名稱、子系統選項
  const getSampleData = async (token) => {
    console.log('getSampleData');
    await axios
      .post(
        `/api/project/post_sample`,
        { project_id: router.query.project_id },
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      )
      .then(async (response) => {
        // console.log('get sample data', response.data.obj);
        await setSampleDataInfo(response.data.obj);
        await setSampleData(JSON.parse(response.data.obj.join_sampledata).slice(0, 5));
        await getSubsystemDatasetOptions(response.data.obj.project_id, response.data.obj.project_eng);
        // handleSampleData(response.data.obj.join_sampledata);
      })
      .catch((error) => {
        // console.log('get sample data error', error);
      });
  };

  // 取得專案資料欄位
  async function getColumnsData(project_id) {
    const config = {
      headers: { Authorization: `Bearer ${session.tocken.loginUserToken}` },
      params: {
        project_id: project_id,
      }
    };
    const promiseResult = await axiosPlus({
      method: 'GET',
      stateArray: null,
      url: '/api/project/get_selectcol',
      config: config,
      showSuccessMsg: false
    });
    if (promiseResult && promiseResult?.status == 200) {
      // console.log("promiseResult",promiseResult)
      setColData(promiseResult.data.obj.report_info)
    } else {
      // console.log("Error", promiseResult)
      console.log("Error")
    }
  }

  useEffect(() => {
    getSampleData(session.tocken.loginUserToken);
    getColumnsData(router.query.project_id)
  }, []);

  // 取得專案資料預覽欄位
  const columns = useMemo(() => {
    let columns = [];
    let columns_selected_temp = {};
    if (sampleData) {
      Object.keys(sampleData[0]).map((c) => {
        columns.push(c);
        columns_selected_temp[c] = false;
      });
    }
    // console.log('columns', columns);
    setColumnsSelected(columns_selected_temp);
    // console.log('columns_selected_temp',columns_selected_temp)

    // 修改 column 欄位
    if(selectedDataset && selectedDataset === 'K匿名強化資料集'){
      columns = colData.k;
    }else if(selectedDataset && selectedDataset === '合成強化資料集'){
      columns = colData.syn;
    }else if(selectedDataset && selectedDataset === '差分強化資料集'){
      columns = colData.dp;
    }

    return columns;
  }, [sampleData,selectedDataset]);

  const handleSelectedDataset = (event) => {
    setSelectedDataset(event.target.value);
  };

  // 執行可用性分析-感興趣欄位payload
  async function handleTargetCols(colsDic) {
    let target_cols = '';
    let count = 0;
    Object.keys(colsDic).map((c) => {
      if (colsDic[c]) {
        if (count >= 3) {
          setPopUpMsg('請選擇一至三個感興趣欄位');
          setPopUp(true);
        }
        if (target_cols !== '') {
          target_cols = target_cols + ',' + c;
        } else {
          target_cols = c;
        }
        count = count + 1;
      }
    });
    if (count === 0) {
      setPopUpMsg('請選擇一至三個感興趣欄位');
      setPopUp(true);
    }
    return { target_cols: target_cols, count: count };
  }
  // 更新專案狀態
  async function handleUpdateStatus() {
    const payloadUpdateStatus = {
      project_id: router.query.project_id,
      status: 8
    };
    const configUpdateStatus = {
      headers: {
        Authorization: `Bearer ${session.tocken.loginUserToken}`
      }
    };
    const promiseUpdateStatus = axiosPlus({
      method: 'PUT',
      stateArray: null,
      url: '/api/project/put_projectStatus',
      payload: payloadUpdateStatus,
      config: configUpdateStatus,
      showSuccessMsg: false
    });
    console.log('promiseUpdateStatus', promiseUpdateStatus);
  }
  // 執行可用性分析
  async function handleExecUtility() {
    // 若未選擇強化資料集就彈出警告
    if (!selectedDataset) {
      setPopUpMsg('尚未選擇強化資料集');
      setPopUp(true);
      return;
    }

    let targetColResult = await handleTargetCols(columnsSelected);
    // 選擇欄位介於 1 ~ 3 才執行可用性分析
    if (1 <= targetColResult.count && targetColResult.count <= 3 && selectedDataset) {
      let payload = {
        project_id: sampleDataInfo.project_id,
        member_id: user.id,
        project_name: sampleDataInfo.project_eng,
        privacy_type: MLUtilityDic[selectedDataset],
        target_cols: targetColResult.target_cols
      };
      // console.log('payload', payload);
      if (targetColResult.target_cols !== '') {
        axios
          .post('/api/project/post_ML_utility', payload, {
            headers: {
              Authorization: `Bearer ${session.tocken.loginUserToken}`
            }
          })
          .then(async (res) => {
            await setPopUpMsg('可用性分析中，依資料大小不同需花費數分鐘到數小時不等，完成後將以狀態顯示。');
            await setPopUp(true);
            if (!wroteLog['ML-Utility']) {
              await petsLog(session, 0, `Login User ${user.account}執行可用性分析`, sampleDataInfo.project_name);
              setWroteLog((prev) => ({ ...prev, ['ML-Utility']: true }));
            }
            await handleUpdateStatus();
            // await setStartUtility(true);
            // console.log('post_ML_utility res', res);
            // updateUtilityStatus(sampleDataInfo.project_id);
          })
          .catch((err) => {
            // console.log(err);
          });
      }
    }
  }

  // 取得可用性分析狀態
  // async function updateUtilityStatus(project_id) {
  //       console.log('check status');
  //       let timer = setTimeout(function() {updateUtilityStatus(project_id)}, 30000);
  //       console.log('reset timer');
  //
  //       let url = '/api/project/get_projectStatus';
  //       const config = {
  //           headers: { Authorization: `Bearer ${session.tocken.loginUserToken}` },
  //           params: {
  //               project_id: project_id,
  //           },
  //       };
  //       const promiseResult = await axiosPlus({
  //           method: "GET",
  //           stateArray: null,
  //           url: url,
  //           config: config,
  //           showSuccessMsg: false,
  //       });
  //       // console.log('promiseResult', promiseResult);
  //
  //       if(promiseResult.data.status === 0) {
  //           if(promiseResult.data.obj.status === 9){
  //               console.log('clear timeout 1');
  //               setReportReady(true);
  //               setStartUtility(false);
  //               clearTimeout(timer);
  //           }else{
  //               console.log('continue timer');
  //               updateUtilityStatus(project_id);
  //           }
  //
  //       }else{
  //           console.log('clear timeout 2');
  //           setStartUtility(false);
  //           clearTimeout(timer);
  //       }
  // }

  // function handleShowReport() {
  //     router.push({
  //         pathname: '/apps/project/utility-report/',
  //         query: {'project_id': sampleDataInfo.project_id}
  //     })
  // }

  return (
    <Page title="MLutility">
      <Grid container spacing={6} sx={{ ml: '50px', maxWidth: '1200px' }}>
        <Grid item>
          <Typography variant="h3" sx={{ marginBottom: '20px' }}>
            可用性分析
          </Typography>
        </Grid>
        <Grid container sx={{ margin: '20px 0 0 50px' }}>
          <Grid item lg={2}>
            <InputLabel>專案名稱</InputLabel>
          </Grid>
          <Grid item lg={8}>
            <TextField
              fullWidth
              value={sampleDataInfo ? sampleDataInfo.project_name : ''}
              InputProps={{ readOnly: true, disableUnderline: true }}
              disabled
              variant="filled"
              onChange={() => {}}
              sx={{
                '& .MuiInputBase-input.Mui-disabled': {
                  backgroundColor: 'disableBGColor',
                  WebkitTextFillColor: '#000000',
                  padding: '10px'
                }
              }}
            />
          </Grid>
        </Grid>

        <Grid container sx={{ margin: '20px 0 0 50px' }}>
          <Grid item lg={2}>
            <InputLabel>專案資料夾</InputLabel>
          </Grid>
          <Grid item lg={8}>
            <TextField
              fullWidth
              value={sampleDataInfo ? sampleDataInfo.project_eng : ''}
              InputProps={{ readOnly: true, disableUnderline: true }}
              disabled
              variant="filled"
              onChange={() => {}}
              sx={{
                '& .MuiInputBase-input.Mui-disabled': {
                  backgroundColor: 'disableBGColor',
                  WebkitTextFillColor: '#000000',
                  padding: '10px'
                }
              }}
            />
          </Grid>
        </Grid>

        <Grid container sx={{ margin: '20px 0 0 50px' }}>
          <Grid item lg={2}>
            <InputLabel>選擇強化資料集</InputLabel>
          </Grid>
          <Grid item lg={8}>
            <Select
              value={selectedDataset}
              displayEmpty
              name="select "
              renderValue={(selected) => {
                return selected;
              }}
              fullWidth
              onChange={handleSelectedDataset}
            >
              {subsystemOptions &&
                subsystemOptions.map((d) => {
                  return <MenuItem value={d}>{d}</MenuItem>;
                })}
            </Select>
          </Grid>
        </Grid>
        {selectedDataset && (
        <Grid container sx={{ margin: '20px 0 0 50px' }}>
          <Grid item lg={2}>
            <InputLabel>感興趣欄位設定</InputLabel>
          </Grid>
          <Grid item lg={10}>
            <MainCard content={false}>
              <ScrollX>
                {columns && sampleData && (
                  <>
                    <ColumnCheckboxTable
                      columns={columns}
                      data={sampleData}
                      columnsSelected={columnsSelected}
                      setColumnsSelected={setColumnsSelected}
                    />
                    {/*<ReactTable columns={columns} data={sampleData} />*/}
                  </>
                )}
              </ScrollX>
            </MainCard>
          </Grid>
        </Grid>
        )}
      </Grid>
      <Box display="flex">
        <Button variant="contained" fullWidth onClick={handleExecUtility} sx={{ width: '150px', margin: '100px' }}>
          執行
        </Button>
      </Box>
      {popUp && (
        <StateControlDialog
          stateArrayOpenControl={[popUp, setPopUp]}
          dialogTitle={null}
          dialogContent={popUpMsg}
          disagreeButtonText={null}
          agreeButtonText="確定"
          agreeButtonOnClick={() => {
            setPopUp(false);
            if (popUpMsg && popUpMsg.includes('可用性分析中')) {
              router.push('/apps/project/projects-table');
            }
          }}
        />
      )}
    </Page>
  );
};

MLUtility.getLayout = function getLayout(page) {
  return <Layout>{page}</Layout>;
};

export default MLUtility;
