import { useContext, useEffect, useMemo, useState } from 'react';
import * as React from 'react';
import PropTypes from 'prop-types';
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
    FormGroup,
    FormControlLabel,
    Checkbox
} from '@mui/material';

// third-party
import axios from 'axios';

// project import
import Layout from 'layout';
import Page from 'components/Page';
import ProjectStepper from 'sections/apps/progress/project_stepper';

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
    });
}

// API: AES Decrypt
const handleSendAesDecrypt = async (event, session, project_id, checkboxCheckedRecord, setSuccessMsg, setErrorMsg) => {
    let aes_col = "";
    for (const key in checkboxCheckedRecord) {
        if (checkboxCheckedRecord[key])
            aes_col = aes_col + key + ",";
    }

    aes_col = aes_col.slice(0, aes_col.length - 1);
    // console.log("Ready send aes_col:", aes_col);

    const payload = {
        project_id: project_id,
        aes_col: aes_col,
    };
    const config = {
        headers: {
            Authorization: `Bearer ${session.tocken.loginUserToken}`
        },
    };
    const promiseResult = await axiosPlus({
        method: "POST",
        stateArray: null,
        url: "/api/project/post_aesDecrypt",
        payload: payload,
        config: config,
        showSuccessMsg: false,
    });

    console.log("[API] AES Decrypt payload", payload);
    console.log("[API] AES Decrypt promiseResult", promiseResult);
    if (promiseResult.data.status == 0) {
        setSuccessMsg(prev => ({ ...prev, ['AesDecrypt']: '成功送出' }));
        setErrorMsg(prev => ({ ...prev, ['AesDecrypt']: null }));
    }
    else {
        setSuccessMsg(prev => ({ ...prev, ['AesDecrypt']: null }));
        setErrorMsg(prev => ({ ...prev, ['AesDecrypt']: `錯誤: ${promiseResult.data.msg}` }));
    }
}

/****************  
 * View-control * 
 ****************/
const DataDecrypt = () => {
    const router = useRouter();
    const { data: session } = useSession();
    const [project_id, setProject_id] = useState(null);
    const [project_name, setProject_name] = useState(null);
    const [system_name, setSystem_name] = useState(null);
    const [sub_system_id, setSub_system_id] = useState(null);
    const [successMsg, setSuccessMsg] = useState({ AesDecrypt: null });
    const [errorMsg, setErrorMsg] = useState({ AesDecrypt: null });

    const [projectStatus, setProjectStatus] = useState(-1);
    const [projectDetail, setProjectDetail] = useState([]);

    const [checkboxCheckedRecord, setCheckboxCheckedRecord] = useState({});

    // First Mount
    useEffect(() => {
        // Get project_id, project_name, system_name
        const _project_id = router.query.project_id;
        setProject_id(_project_id);
        setProject_name(router.query.project_name);
        setSystem_name(router.query.system_name);
        setSub_system_id(router.query.sub_system_id);

        // Update project status
        handleFetchProjectStatus(session, _project_id, setProjectStatus);
        // Fetch API /projects/detail
        handleFetchProjectDetail(session, _project_id, [projectDetail, setProjectDetail]);
    }, []);

    // Show aes columns
    useEffect(() => {
        console.log("projectDetail.aes_col:", projectDetail.aes_col);
    }, [projectDetail]);

    // Show checkbox status
    useEffect(() => {
        console.log("checkbox stauts:", checkboxCheckedRecord);
    }, [checkboxCheckedRecord]);

    // Handle onChange event of checkbox checking
    const handleCheckboxChange = (event) => {
        // console.log(`${event.target.name}:`, event.target.checked);
        setCheckboxCheckedRecord({
            ...checkboxCheckedRecord,
            [event.target.name]: event.target.checked,
        });
    };

    // Component: checking box
    const checkboxAES = (stringAesColumns) => {
        if (stringAesColumns) {
            const aesList = stringAesColumns.split(",");
            // console.log("aesList", aesList);
            return (
                <FormGroup>
                    {aesList.map((element, index) => (<FormControlLabel label={element} control={<Checkbox onChange={handleCheckboxChange} name={element} />} />))}
                    {/* <FormControlLabel control={<Checkbox defaultChecked />} label="Label" /> */}
                    {/* <FormControlLabel required control={<Checkbox />} label="Required" /> */}
                    {/* <FormControlLabel disabled control={<Checkbox />} label="Disabled" /> */}
                </FormGroup>
            );
        }
        else
            return <></>;
    }

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

            {/* 頁面標題 */}
            <Box sx={{ width: '100%', mb: "20px", mt: "50px" }}>
                <Stack direction="column" spacing={1} sx={{ minWidth: '90%' }}>
                    <Typography variant='h3'>資料解密</Typography>
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
                                InputProps={{ readOnly: true, }}
                                disabled
                                color="secondary"
                            />
                        </Grid>
                    </Grid>
                </Grid>
            </Box>

            <Typography variant='h4'>選擇AES解密欄位</Typography>
            <Box sx={{ ml: "10px", }}>
                {checkboxAES(projectDetail.aes_col)}
            </Box>


            {/* 按鈕 */}
            <Box
                m={1}
                display="flex"
                justifyContent="flex-front"
                alignItems="flex-end"
            >
                <Button variant="contained" onClick={(e) => {handleSendAesDecrypt(e, session, project_id, checkboxCheckedRecord, setSuccessMsg, setErrorMsg)}}   >
                    進行解密
                </Button>
            </Box>

            {/* 結果訊息 */}
            <Box sx={{ ml: "10px", }}>
                {(errorMsg.AesDecrypt) ? <Typography color="red">{errorMsg.AesDecrypt}</Typography> : <Typography color="green">{successMsg.AesDecrypt}</Typography>}
            </Box>
        </Page >
    );
};

DataDecrypt.getLayout = function getLayout(page) {
    return <Layout>{page}</Layout>;
};

export default DataDecrypt;