import PropTypes from 'prop-types';
import { useContext, useEffect, useMemo, useState } from 'react';
import * as React from 'react';
import axiosPlus from 'sections/api/axiosPlus';

// next
import { useSession, } from 'next-auth/react';
import { useRouter } from 'next/router';

// material-ui
import { useTheme } from '@mui/material/styles';
import {
    Box,
    Button,
    Divider,
    Grid,
    InputLabel,
    Stack,
    TextField,
    Typography,
    ListItem,
    ListItemButton,
    ListItemText,
    Paper,
    Link
} from '@mui/material';
import AttachFileIcon from '@mui/icons-material/AttachFile';

// third-party
import axios from 'axios';

// project import
import Layout from 'layout';
import Page from 'components/Page';
import DownloadFiles from "../../../sections/apps/data-connect/download-files";
import ProjectStepper from 'sections/apps/progress/project_stepper';
import { mockDownloadFiles } from '../../../utils/mock-download-files';

/***********
 * Control * 
 ***********/
// API: fetch project status (/api/projects/status)
const handleFetchProjectStatus = async (session, projectID, setProjectStatus) => {
    const config = {
        headers: {
            Authorization: `Bearer ${session.tocken.loginUserToken}`,
        },
        params: {
            project_id: projectID,
        },
    };
    const promiseResult = await axiosPlus({
        method: "GET",
        stateArray: null,
        url: "/api/project/get_projectStatus",
        config: config,
        showSuccessMsg: false,
    });

    if (promiseResult && promiseResult?.status == 200)
        setProjectStatus(promiseResult.data.obj.status);
}

// API: list directory at server-side
const handleFetchDirList = async (targetDir, setDataList, whom, seterrorMsg) => {
    const promiseResult = await axiosPlus({
        method: "GET",
        stateArray: null,
        url: "/api/download/get_listDir",
        config: { params: { targetDir: targetDir } },
        showSuccessMsg: false,
    });

    // console.log("[handleListDir] promiseResult.data:", promiseResult.data);

    if (promiseResult.request.status == 200) {
        if (promiseResult.data.status == 1) {
            seterrorMsg(prev => ({ ...prev, [whom]: null }));
            setDataList(promiseResult.data.obj);
        }
        else if (promiseResult.data.status == 0) {
            // seterrorMsg(prev => ({ ...prev, [whom]: `錯誤: 資料夾不存在 ${promiseResult.data.msg}` }));
            seterrorMsg(prev => ({ ...prev, [whom]: null }));
            setDataList([]);
        }
        else {
            console.log("[API] GET ListDir ERROR", promiseResult);
            seterrorMsg(prev => ({ ...prev, [whom]: `錯誤: 不明錯誤 ${promiseResult.data.msg}` }));
            setDataList([]);
        }
    }
    else {
        console.log("[API] GET ListDir UNKNOWN ERROR", promiseResult);
        seterrorMsg(prev => ({ ...prev, [whom]: `錯誤: 不明錯誤` }));
        setDataList([]);
    }
};

const handleDownloadCSV = async (event, downloadFileName, downloadURL) => {
    // console.log("[handleDownloadCSV] downloadURL:", downloadURL);

    // API: request Next.js server csv file 
    console.log(downloadURL);
    const response = await axiosPlus({
        method: "POST",
        stateArray: null,
        url: "/api/download/post_readStreamCSV",
        payload: { url: downloadURL },
        config: {},
        showSuccessMsg: false,
    });

    console.log("[handleDownloadCSV] response:", response);

    const blob = new Blob([response.data], { type: "text/csv" });
    const link = document.createElement("a");
    link.href = window.URL.createObjectURL(blob);
    link.download = downloadFileName;
    document.body.appendChild(link);
    link.click();
};

// Preprocess download_files_API
const preprocessedAPI = (api_obj) => {
    let preprocessedArray = [];
    api_obj.map((element, index) => {
        if (element.fileName.endsWith(`.csv`)) {
            preprocessedArray.push({
                'button_name': element.fileName,
                'file_name': element.fileName,
                'url': element.url,
                'icon': <AttachFileIcon sx={{ fontSize: 20, transform: 'rotate(45deg)' }} />,
                'behavior': 'exeClickFunc',
                'clickFunc': (e) => { handleDownloadCSV(e, element.fileName, element.url) },
                'disabled': false,
            });
        }
    });
    return preprocessedArray;
}

// systemName mapping table
const systemName2systemFolderName = {
    'KAnonymous': 'k',
    'syntheticData': 'syn',
    'differentialPrivacy': 'dp',
}

/****************  
 * View-control * 
 ****************/
const DataDownload = () => {
    const { data: session } = useSession();
    const router = useRouter();
    const [projectID, setProjectID] = useState(null);
    const [projectName, setProjectName] = useState(null);
    const [systemName, setSystemName] = useState(null);
    const [projectEngName, setProjectEngName] = useState(null);
    const [subSystemID, setSubSystemID] = useState(null);
    const [gotQuery, setGotQuery] = useState(false);
    const [projectStatus, setProjectStatus] = useState(-1);
    const [encdata, setEncData] = useState([]);
    const [dncdata, setDncData] = useState([]);
    const [errorMsg, seterrorMsg] = useState({ enc: null, dec: null });

    // Mounting effect
    useEffect(() => {
        // Get projectID, projectName ...
        const _projectID = router.query.project_id;
        setProjectID(_projectID);
        setProjectName(router.query.project_name);
        setSystemName(router.query.system_name);
        setProjectEngName(router.query.project_eng_name);
        setSubSystemID(router.query.sub_system_id);

        // API /projects/status
        handleFetchProjectStatus(session, _projectID, setProjectStatus);

        setGotQuery(true);
    }, []);

    useEffect(() => {
        if (gotQuery) {
            // API /download/get_listDir
            handleFetchDirList(`download_folder/enc/${systemName2systemFolderName[systemName]}/${projectEngName}`, setEncData, 'enc', seterrorMsg);
            handleFetchDirList(`download_folder/dec/${systemName2systemFolderName[systemName]}/${projectEngName}`, setDncData, 'dec', seterrorMsg);
        }
    }, [gotQuery]);

    /******** 
     * View * 
     ********/
    return (
        <Page title="Customer List">
            {/* 頂部進度條 */}
            <Box sx={{ width: '100%', mb: "20px", mt: "50px", ml: "50px", alignItems: "center" }} >
                <Box sx={{ width: "60%", alignItems: "center" }} >
                    <ProjectStepper currentStep={projectStatus} terminatedStep={null} />
                </Box>
            </Box>

            <Box sx={{ width: '100%', mb: "20px", mt: "50px" }}>
                <Grid container spacing={1} sx={{ ml: "50px" }}>
                    <Stack direction="column" spacing={1} sx={{ minWidth: '90%' }}>
                        {/* 頁面標題 */}
                        <Grid container item>
                            <Typography variant='h3'>下載資料集</Typography>
                        </Grid>

                        <Divider />

                        <Grid container item>
                            <Grid item lg={2}>
                                <InputLabel sx={{ textAlign: { xs: 'left', sm: 'left', ml: "250px" } }}>專案名稱</InputLabel>
                            </Grid>
                            <Grid item lg={8}>
                                <TextField
                                    fullWidth
                                    value={projectName}
                                    InputProps={{ readOnly: true, }}
                                    disabled
                                    color="secondary"
                                />
                            </Grid>
                        </Grid>

                        {/* 下載列表 */}
                        {(systemName == "KAnonymous") ?
                            <>
                                {/* K匿名 (有解密列表) */}
                                <Typography variant='h4'>資料解密前</Typography>
                                {(errorMsg.enc) ? <>{errorMsg.enc} </> :
                                    (encdata.length) ? <>
                                        <DownloadFiles height={180} argArray={preprocessedAPI(encdata)} />
                                    </> : <>
                                        {"尚無資料"}
                                    </>}

                                <Typography variant='h4'>資料解密後</Typography>
                                {(errorMsg.dec) ? <>{errorMsg.dec}  </> :
                                    (dncdata.length) ? <>
                                        <DownloadFiles height={180} argArray={preprocessedAPI(dncdata)} />
                                    </> : <>
                                        {"尚無資料"}
                                    </>}
                            </> :
                            <>
                                {/* 生成&差分 (無解密列表) */}
                                {(errorMsg.enc) ? <>{errorMsg.enc} </> :
                                    (encdata.length) ? <>
                                        <DownloadFiles height={180} argArray={preprocessedAPI(encdata)} />
                                    </> : <>
                                        {"尚無資料"}
                                    </>}
                            </>
                        }
                    </Stack>
                </Grid>
            </Box>
        </Page>
    )
}

DataDownload.getLayout = function getLayout(page) {
    return <Layout>{page}</Layout>;
};

export default DataDownload;