// next
import { useSession } from 'next-auth/react';

/**
 * Function : useUser(登入的使用者資訊)
 *
 * @returns {object} id: 使用者id account: 使用者帳戶名稱
*/
const useUser = () => {
  const { data: session } = useSession();

  // console.log('session', session);

  if (session) {
    // const user = session?.user;
    const user = session?.tocken;
    
    // const provider = session?.provider;
    // let thumb = user?.image;
    // if (provider === 'cognito') {
    //   const email = user?.email?.split('@');
    //   user.name = email ? email[0] : 'Jone Doe';    }

    // if (!user?.image) {
    //   user.image = '/assets/images/users/avatar-1.png';
    //   thumb = '/assets/images/users/avatar-thumb-1.png';
    // }

    const newUser = {
      id: user.id,
      account: user.account,
    };
  
    // fetchUserInfo(user, newUser);

    return newUser;

  }

  return false;
};

// const fetchUserInfo = async (user, newUser) => {
//   try {
//     const response = await axios.get(`/api/user/get_info/${user.id}`, {
//       headers: {
//         Authorization: `Bearer ${user.loginUserToken}`
//       }
//     });

//     newUser.account = response.data.obj.useraccount;

//   } catch (error) {
//     console.error("Error fetching user info:", error);
//     return newUser;
//   }
// };

export default useUser;
