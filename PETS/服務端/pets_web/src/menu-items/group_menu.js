// third-party
import BusinessOutlinedIcon from '@mui/icons-material/BusinessOutlined';
import { FormattedMessage } from 'react-intl';

// ==============================|| MENU ITEMS - GROUP ||============================== //

const groupMenu = {
  id: '2',
  title: <FormattedMessage id=" " />,
  type: 'group',
  children: [
    {
      id: 'groupList',
      title: <FormattedMessage id="單位管理" />,
      type: 'item',
      url: '/apps/group/groups-table',
      breadcrumbs: true,
      icon: BusinessOutlinedIcon
    }
  ]
};

export default groupMenu;
