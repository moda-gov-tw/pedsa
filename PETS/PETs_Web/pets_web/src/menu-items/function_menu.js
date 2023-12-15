// material-ui
// import ManageAccountsOutlinedIcon from '@mui/icons-material/ManageAccountsOutlined';
// import SupervisedUserCircleOutlinedIcon from '@mui/icons-material/SupervisedUserCircleOutlined';
// import PermDataSettingOutlinedIcon from '@mui/icons-material/PermDataSettingOutlined';

// third-party
import { FormattedMessage } from 'react-intl';

// icons
// const icons = {
//   ManageAccountsOutlinedIcon,
//   SupervisedUserCircleOutlinedIcon,
//   PermDataSettingOutlinedIcon
// };

// ==============================|| MENU ITEMS - APPLICATIONS ||============================== //

const functions = {
  id: 'group-admin',
  title: <FormattedMessage id=" " />,
  type: 'group',
  children: [
    {
      id: 'projectList',
      title: <FormattedMessage id="專案列表" />,
      type: 'item',
      url: '/apps/project/projects-table',
      // icon: icons.ManageAccountsOutlinedIcon,
      breadcrumbs: true
    },
    {
      id: 'newProject',
      title: <FormattedMessage id="建立專案及設定" />,
      type: 'not-show',
      url: '/apps/project/new-project',
      // icon: icons.ManageAccountsOutlinedIcon,
      breadcrumbs: false
    },
    {
      id: 'groupList',
      title: <FormattedMessage id="單位管理" />,
      type: 'item',
      url: '/apps/group/groups-table',
      // icon: icons.SupervisedUserCircleOutlinedIcon,
      breadcrumbs: true
    },
    {
      id: 'user',
      title: <FormattedMessage id="人員管理" />,
      type: 'item',
      url: '/apps/user/users-table',
      breadcrumbs: true
    },
    {
      id: 'systemInfo',
      title: <FormattedMessage id="系統資訊" />,
      type: 'collapse',
      // breadcrumbs: true,
      children: [
        {
          id: 'sys-health-test',
          title: <FormattedMessage id="健康檢測" />,
          type: 'item',
          url: '/apps/system/health-test'
        },
        {
          id: 'sys-log-record',
          title: <FormattedMessage id="系統操作紀錄查詢" />,
          type: 'item',
          url: '/apps/system/log-record'
        }
      ]
    },
  ]
};

export default functions;

