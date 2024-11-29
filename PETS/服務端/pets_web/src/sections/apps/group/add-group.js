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
  Stack,
  TextField,
  Tooltip,
} from '@mui/material';
import { LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';

// third-party
import axios from 'axios';
import _ from 'lodash';
import * as Yup from 'yup';
import { useFormik, Form, FormikProvider } from 'formik';

// project imports
import useUser from "hooks/useUser";
import { openSnackbar } from 'store/reducers/snackbar';
import { checkGroupName, checkGroupType, checkGroupQuota } from 'utils/check-rules';
import petsLog from "../logger/insert-system-log";

// assets
import { ConfigContext } from "../../../contexts/ConfigContext";
import { checkUsername } from "../../../utils/check-rules";

// constant
const getInitialValues = (group) => {
  const newGroup = {
    group_name: '',
    group_type: '',
    project_quota: '',
  };
  if (group) {
    return _.merge({}, newGroup, group);
  }
  return newGroup;
};

// ==============================|| GROUP ADD / EDIT ||============================== //
/**
 * Function: AddGroup
 *
 * Child component of GroupListTable
 *
 * @param {{ group: object, groupId: number, allGroups: object, setAllGroups: func, onCancel: func }} argObject
 * * `group`: value of current selected group.
 * * `groupId`: value of current selected group id.
 * * `allGroups`: list of all group(state).
 * * `setAllGroups`: function to update allGroups.
 * * `onCancel`: function to control dialog open/close.
 *
 * @returns {JSX.Element}
 */
const AddGroup = ({ group, groupId, allGroups, setAllGroups, onCancel }) => {
  const { data: session } = useSession();
  const user = useUser();
  const CancelToken = axios.CancelToken;
  const source = CancelToken.source();  // 取消api

  const dispatch = useDispatch();
  const [wroteLog, setWroteLog] = useState({});

  const GroupSchema = Yup.object().shape({
    group_name: Yup.string(),
    group_type: Yup.string(),
    project_quota: Yup.number(),
  });

  const formik = useFormik({
    initialValues: getInitialValues(group),
    validationSchema: GroupSchema,
    onSubmit: async (values, { setSubmitting }) => {

      if(checkGroupType(values.group_type) || checkGroupName(values.group_name) || checkGroupQuota(values.project_quota)) {
        setSubmitting(false);
        dispatch(
          openSnackbar({
            open: true,
            message: '請確認所有欄位皆符合要求',
            variant: 'alert',
            alert: {
              color: 'error'
            },
            close: false
          })
        );
        return;
      }

      try {
        // console.log('submit values', values);
        if (group) {
          await handleEditGroup();
        } else {
          await handleCreateGroup();
        }
        setSubmitting(false);
        // onCancel();
      } catch (error) {
        // console.error(error);
      }
    }
  });
  const { values, errors, touched, handleSubmit, isSubmitting, getFieldProps, setFieldValue } = formik;
  // console.log('formik.values', values);

  async function appendData(newGroupData) {
    await setAllGroups([...allGroups, { ...newGroupData }]);
  }


  // 更新單位列表裡的資料
  async function updateData(newGroupData) {
    let index = allGroups.findIndex(function (temp) {
      return temp.group_name === group.group_name;
    });
    let updatedGroupData = { ...allGroups[index], ...newGroupData };
    // console.log('updatedGroupData', updatedGroupData);
    const newAllGroups = [
      ...allGroups.slice(0, index),
      updatedGroupData,
      ...allGroups.slice(index + 1)
    ];
    await setAllGroups(newAllGroups);
  }

  // 新增單位
  async function handleCreateGroup() {
    await axios.post('/api/group/create_group/', {
      'group_name': values.group_name.trim(),
      'group_type': values.group_type.trim(),
      'project_quota': values.project_quota.trim(),
    },
      {
        headers: {
          Authorization: `Bearer ${session.tocken.loginUserToken}`
        }
      })
      .then(async (response) => {
        await appendData(response.data.obj);
        if (!wroteLog["addGroup"]) {
          await petsLog(session, 0, `Login User ${user.account}建立新單位${values.group_name}成功`);
          setWroteLog(prev => ({ ...prev, ["addGroup"]: true }))
        }
        dispatch(
            openSnackbar({
              open: true,
              message: '新增單位成功',
              variant: 'alert',
              alert: {
                color: 'success'
              },
              close: false
            })
          );
        await onCancel();
      })
      .catch(async (error) => {
        if (!wroteLog["addGroup"]) {
          await petsLog(session, 0, `Login User ${user.account}建立新單位${values.group_name}失敗`);
          setWroteLog(prev => ({ ...prev, ["addGroup"]: true }))
        }
        dispatch(
            openSnackbar({
              open: true,
              message: '新增單位失敗，單位代碼及單位名不可重複',
              variant: 'alert',
              alert: {
                color: 'error'
              },
              close: false
            })
          );
        // console.log('error', error);
      });
  }

  // 編輯單位
  async function handleEditGroup() {
    let newGroupData = Object.fromEntries(Object.entries(formik.values).filter(([key]) => !key.includes('group_type')));
    await axios.put(`/api/group/edit/${groupId}`,
      newGroupData,
      {
        headers: {
          Authorization: `Bearer ${session.tocken.loginUserToken}`
        }
      })
      .then(async () => {
        await updateData(newGroupData);
        if (!wroteLog["editGroup"]) {
          await petsLog(session, 0, `Login User ${user.account}編輯單位${values.group_name}成功`);
          setWroteLog(prev => ({ ...prev, ["editGroup"]: true }))
        }
        dispatch(
          openSnackbar({
            open: true,
            message: '編輯單位成功',
            variant: 'alert',
            alert: {
              color: 'success'
            },
            close: false
          })
        );
        await onCancel();
      })
      .catch(async (error) => {
        dispatch(
          openSnackbar({
            open: true,
            message: '編輯單位失敗，請確認單位是否已存在',
            variant: 'alert',
            alert: {
              color: 'error'
            },
            close: false
          })
        );
        if (!wroteLog["editGroup"]) {
          await petsLog(session, 0, `Login User ${user.account}編輯單位${values.group_name}失敗`);
          setWroteLog(prev => ({ ...prev, ["editGroup"]: true }))
        }
        // console.log('error', error);
      })
  }

  return (
    <>
      <FormikProvider value={formik}>
        <LocalizationProvider dateAdapter={AdapterDateFns}>
          <Form autoComplete="off" noValidate onSubmit={handleSubmit}>
            {/*彈出視窗為新增單位或是編輯單位*/}
            <DialogTitle>{group ? '編輯單位' : '新增單位'}</DialogTitle>
            <Divider />
            <DialogContent sx={{ p: 2.5 }}>
              <Grid container spacing={3}>
                <Grid item xs={12} md={8}>
                  <Grid container spacing={3}>

                    {/*單位名文字框*/}
                    <Grid item xs={12}>
                      <Stack spacing={1.25}>
                        <InputLabel htmlFor="group-name">*單位名</InputLabel>
                        <TextField
                          fullWidth
                          id="group-name"
                          placeholder=""
                          {...getFieldProps('group_name')}
                          label={checkGroupName(values.group_name) && '只可以包含中英文字元及底線'}
                          error={checkGroupName(values.group_name)}
                          // error={Boolean(touched.group_name && errors.group_name)}
                          helperText={touched.group_name && errors.group_name}
                        />
                      </Stack>
                    </Grid>

                    {/*單位代號文字框*/}
                    <Grid item xs={12}>
                      <Stack spacing={1.25}>
                        <InputLabel htmlFor="group-type">*單位代號</InputLabel>
                        <TextField
                          fullWidth
                          id="group-type"
                          placeholder=""
                          {...getFieldProps('group_type')}
                          disabled={!!group}
                          label={checkGroupType(values.group_type) && '不可包含中文字元及任何特殊字元，且字數上限為5'}
                          error={checkGroupType(values.group_type)}
                          // error={Boolean(touched.group_type && errors.group_type)}
                          helperText={touched.group_type && errors.group_type}
                        />
                      </Stack>
                    </Grid>

                    {/*單位專案總量文字框*/}
                    <Grid item xs={12}>
                      <Stack spacing={1.25}>
                        <InputLabel htmlFor="project-quota">*專案總量</InputLabel>
                        <TextField
                          fullWidth
                          id="project-quota"
                          placeholder=""
                          {...getFieldProps('project_quota')}
                          label={checkGroupQuota(values.project_quota) && '只能是數字'}
                          error={checkGroupQuota(values.project_quota)}
                          // error={Boolean(touched.project_quota && errors.project_quota)}
                          helperText={touched.project_quota && errors.project_quota}
                        />
                      </Stack>
                    </Grid>
                  </Grid>
                </Grid>
              </Grid>
            </DialogContent>
            <Divider />

            {/*確定/取消按鈕*/}
            <DialogActions sx={{ p: 2.5 }}>
              <Grid container justifyContent="space-between" alignItems="center">
                <Grid item>
                  <Stack direction="row" spacing={2} alignItems="center">
                    <Button sx={{ minWidth: '100px' }} color="error" onClick={onCancel}>
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
      </FormikProvider>
      {/*{!isCreating && <AlertCustomerDelete title={user.fatherName} open={openAlert} handleClose={handleAlertClose} />}*/}
    </>
  );
};

AddGroup.propTypes = {
  user: PropTypes.any,
  onCancel: PropTypes.func
};

export default AddGroup;
