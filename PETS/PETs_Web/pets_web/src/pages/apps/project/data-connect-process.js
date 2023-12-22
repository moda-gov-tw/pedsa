import { useContext, useEffect, useMemo, useState } from 'react';
import * as React from 'react';
import PropTypes from 'prop-types';
import useClock from 'hooks/useClock';
import axiosPlus from 'sections/api/axiosPlus';

// next
import { useSession, } from 'next-auth/react';
import { useRouter } from 'next/router';

// material-ui
import {
    Box,
    Button,
    Divider,
    Grid,
    Stack,
    InputLabel,
    TextField,
    Typography,
} from '@mui/material';

// third-party
import axios from 'axios';

// project import
import Layout from 'layout';
import Page from 'components/Page';
// import DoubleCircularProgress from 'sections/apps/progress/double-circular-progress';
import DoubleCircularProgressPure from 'sections/apps/progress/double-circular-progress-pure';
import ProjectStepper from 'sections/apps/progress/project_stepper';
// import { mockProgress } from '../../../utils/mock-progress';
import StateControlDialog from 'sections/apps/Dialog/state-dialog';
import useUser from "hooks/useUser";
import petsLog from "../../../sections/apps/logger/insert-system-log";

/*********** 
 * Control * 
 ***********/
// API: fetch project status (/api/projects/status)
const handleFetchProjectStatus = async (session, project_id, setProjectStatus) => {
    const config = {
        headers: {
            Authorization: `Bearer ${session.tocken.loginUserToken}`,
        },
        params: {
            project_id: project_id,
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

// API: set new project status (/api/project/put_projectStatus)
const handleSetProjectStatus = async (session, project_id, newStatus, setResponseChangeProjectStatus, setErrorMsg) => {
    const payload = {
        project_id: project_id,
        status: newStatus,
    };
    const config = {
        headers: {
            Authorization: `Bearer ${session.tocken.loginUserToken}`
        },
    };
    axiosPlus({
        method: "PUT",
        stateArray: null,
        url: "/api/project/put_projectStatus",
        payload: payload,
        config: config,
        showSuccessMsg: false,
    }).then((response) => {
        // console.log("promiseUpdateStatus", response);
        if (response) {
            const status = response.data.status;
            if (status != 1) {
                console.log("專案狀態更新時發生錯誤 /projects/status (put) -> response.data.msg", response.data.msg);
                setErrorMsg(prev => ({ ...prev, ["updateStatus"]: "專案狀態更新時發生錯誤" }));
            }
            setResponseChangeProjectStatus(status);
        }
    })
}

// API: fetch project detail (/api/projects/detail)
const handleFetchProjectDetail = async (session, project_id, [projectDetail, setProjectDetail]) => {
    const payload = {
        project_id: project_id,
    };
    const config = {
        headers: {
            Authorization: `Bearer ${session.tocken.loginUserToken}`
        },
    };
    axiosPlus({
        method: "POST",
        stateArray: [projectDetail, setProjectDetail],
        url: "/api/project/post_projectDetail",
        payload: payload,
        config: config,
        showSuccessMsg: false,
    })
        .then((response) => {
            console.log("projectDetail:", response);
        })
}

// API: Request /projects/join (origin safelink)
const handleProjectJoin = async (session, projectDetail, setJoinStatus, setErrorMsg) => {
    const newArray = [];
    for (let i = 0; i < projectDetail.join_func.length; i++) {
        const obj = projectDetail.join_func[i];
        newArray.push({
            "left_dataset": obj.left_datasetname,
            "left_col": obj.left_col,
            "right_dataset": obj.right_datasetname,
            "right_col": obj.right_col,
        });
    }

    const payload = {
        member_id: session.tocken.id,
        project_id: projectDetail.project_id,
        enc_key: projectDetail.enc_key,
        join_type: projectDetail.join_type,
        join_func: newArray,
    };
    const config = {
        headers: {
            Authorization: `Bearer ${session.tocken.loginUserToken}`
        },
    };
    const promise = axiosPlus({
        method: "POST",
        stateArray: null,
        url: "/api/project/post_projectJoindata",
        payload: payload,
        config: config,
        showSuccessMsg: false,
    });
    promise.then((response) => {
        // console.log("!!!!!!!!!!Join response", response);
        const status = response.data.status;
        if (status != 0) {
            console.log("資料鍵結時發生錯誤 /projects/joindata -> response.data.msg", response.data.msg);
            setErrorMsg(prev => ({ ...prev, ["join"]: "要求執行資料鍵結時發生錯誤" }));
        }
        setJoinStatus(status);
    })
}

const handleBackToDataCheckPage = async (event, router, project_id, project_name) => {
    // Fail & back to previous page
    router.push({
        pathname: '/apps/project/data-check',
        query: {
            project_id: project_id,
            project_name: project_name,
        }
    });
}

/****************  
 * View-control * 
 ****************/
const DataConnectProcess = () => {
    const router = useRouter();
    const { data: session } = useSession();
    const user = useUser();
    const [project_id, setProject_id] = useState(null);
    const [project_name, setProject_name] = useState(null);
    const [projectStatus, setProjectStatus] = useState(-1);
    const [projectDetail, setProjectDetail] = useState(null);
    const [joinStatus, setJoinStatus] = useState(999);
    const [openWarningDialog, setOpenWarningDialog] = useState(false);
    const [responseChangeProjectStatus, setResponseChangeProjectStatus] = useState(999);
    const [errorMsg, setErrorMsg] = useState({ final: "" });
    const [wroteLog, setWroteLog] = useState({});

    // Mount: Get project_id, project_name
    useEffect(() => {
        const _project_id = router.query.project_id;
        setProject_id(_project_id);
        setProject_name(router.query.project_name);
        handleFetchProjectStatus(session, _project_id, setProjectStatus);
        handleFetchProjectDetail(session, _project_id, [projectDetail, setProjectDetail]);
    }, []);

    // Request API /projects/join
    useEffect(() => {
        if (projectDetail && (joinStatus == 999))
            handleProjectJoin(session, projectDetail, setJoinStatus, setErrorMsg);
        if (!wroteLog["dataConnect"]) {
            petsLog(session, 0, `Login User ${user.account} 執行資料安全鏈結`, project_name);
            setWroteLog(prev => ({ ...prev, ["dataConnect"]: true }))
        }
    }, [projectDetail])

    // Check join post response. if send success, change project status to next stage, else ready to show fail dialog.
    useEffect(() => {
        if (joinStatus < 999) {
            if (joinStatus == 0) {
                console.log("Join API success.")
                // Update new project status
                handleSetProjectStatus(session, project_id, 3, setResponseChangeProjectStatus, setErrorMsg);
                // Update current status showing in stepper
                handleFetchProjectStatus(session, project_id, setProjectStatus);
            }
            else {
                console.log(`Join API fail. status is ${joinStatus}`);
            }
        }
    }, [joinStatus])

    useEffect(() => {
        // Check response of join & project status update
        if (joinStatus < 999 && responseChangeProjectStatus < 999) {
            if (joinStatus == 0 && responseChangeProjectStatus == 1) {
                // Jump to projects-table page
                router.push("/apps/project/projects-table");
            }

            if (errorMsg["updateStatus"] || errorMsg["join"]) {
                let finalErrorMsg = "";
                for (const key in errorMsg)
                    finalErrorMsg = finalErrorMsg + errorMsg[key] + "\n";
                setErrorMsg({ final: finalErrorMsg });
                setOpenWarningDialog(true);
            }
        }
    }, [responseChangeProjectStatus, errorMsg])


    /******** 
     * View * 
     ********/
    return (
        <Page title="Customer List">
            {/* 頂部進度條 */}
            <Box sx={{ width: '750px',  margin:"20px auto 60px auto" }} >
                <Box sx={{ width: "100%", alignItems: "center" }} >
                    <ProjectStepper currentStep={projectStatus} terminatedStep={null} />
                </Box>
            </Box>

            {/* 頁面標題 */}
            <Box sx={{ width: '100%', mb: "20px", mt: "50px" }}>
                <Stack direction="column" spacing={1} sx={{ minWidth: '90%' }}>
                    <Typography variant='h3'>資料鍵結處理</Typography>
                    <Divider />
                </Stack>
            </Box >

            <Box sx={{ mt: 5, mb: "20px", ml: "50px", }} >
                <Grid container item spacing={3}>
                    <Grid container spacing={12} >
                        <Grid item lg={2}>
                            <InputLabel sx={{ textAlign: { xs: 'left', sm: 'left', ml: "250px" } }} >專案名稱</InputLabel>
                        </Grid>
                        <Grid item lg={8}>
                            <TextField
                                fullWidth
                                value={project_name}
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
            </Box>

            {/* 圓圈載入動畫 */}
            <Box sx={{ mt: 20, mb: 22 }} >
                <DoubleCircularProgressPure animationDuration="550ms" animationDurationOutter="700ms" />
            </Box>

            {/* 按鈕 */}
            <Box
                m={1}
                display="flex"
                justifyContent="flex-end"
                alignItems="flex-end"
            >
                <Button
                    variant="contained"
                    onClick={() => {
                        router.push('/apps/project/projects-table');
                    }}
                >
                    回到專案列表
                </Button>
            </Box>

            {/* 失敗對話框 */}
            {(openWarningDialog) ? <>
                <StateControlDialog stateArrayOpenControl={[openWarningDialog, setOpenWarningDialog]}
                    dialogTitle={"錯誤"} dialogContent={errorMsg.final}
                    disagreeButtonText={null} agreeButtonText={"回到上一步"}
                    agreeButtonOnClick={(event) => handleBackToDataCheckPage(event, router, project_id, project_name)} />
            </> : <></>}
        </Page >
    )
}

DataConnectProcess.getLayout = function getLayout(page) {
    return <Layout>{page}</Layout>;
};

export default DataConnectProcess;