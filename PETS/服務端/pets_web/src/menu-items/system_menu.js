// third-party
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import DnsOutlinedIcon from '@mui/icons-material/DnsOutlined';
import ManageSearchOutlinedIcon from '@mui/icons-material/ManageSearchOutlined';
import ContentPasteSearchOutlinedIcon from '@mui/icons-material/ContentPasteSearchOutlined';
import FactCheckOutlinedIcon from '@mui/icons-material/FactCheckOutlined';

import { FormattedMessage } from 'react-intl';

// ==============================|| MENU ITEMS - SYSTEM ||============================== //

const sysMenu = {
  id: '4',
  title: <FormattedMessage id=" " />,
  type: 'group',
  children: [
    {
      id: 'systemInfo',
      title: <FormattedMessage id="系統資訊" />,
      type: 'collapse',
      // breadcrumbs: true,
      icon: InfoOutlinedIcon,
      children: [
        {
          id: 'sys-health-test',
          title: <FormattedMessage id="系統容器健康檢測" />,
          type: 'item',
          url: '/apps/system/health-test',
          icon: DnsOutlinedIcon
        },
        {
          id: 'file-permission-compare',
          title: <FormattedMessage id="系統資料夾權限比對" />,
          type: 'item',
          url: '/apps/system/file-permission',
          icon: FactCheckOutlinedIcon
        },
        {
          id: 'sys-log-record',
          title: <FormattedMessage id="使用者操作記錄查詢" />,
          type: 'item',
          url: '/apps/system/log-record',
          icon: ContentPasteSearchOutlinedIcon
        },
        {
          id: 'job-log-record',
          title: <FormattedMessage id="專案操作記錄查詢" />,
          type: 'item',
          url: '/apps/project/job-log-table',
          icon: ManageSearchOutlinedIcon
        }
      ]
    }
  ]
};

export default sysMenu;
