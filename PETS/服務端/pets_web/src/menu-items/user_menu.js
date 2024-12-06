// third-party
import ManageAccountsOutlinedIcon from '@mui/icons-material/ManageAccountsOutlined';
import { FormattedMessage } from 'react-intl';

// ==============================|| MENU ITEMS - USER ||============================== //

const userMenu = {
  id: '3',
  title: <FormattedMessage id=" " />,
  type: 'group',
  children: [
    {
      id: 'user',
      title: <FormattedMessage id="人員管理" />,
      type: 'item',
      url: '/apps/user/users-table',
      breadcrumbs: true,
      icon: ManageAccountsOutlinedIcon
    }
  ]
};

export default userMenu;
