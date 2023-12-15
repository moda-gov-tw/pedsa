
// third-party
import { FormattedMessage } from 'react-intl';

// ==============================|| MENU ITEMS - USER ||============================== //

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

export default sysMenu;

