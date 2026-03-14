import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const LoginPage = () => {
	const [username, setUsername] = useState('');
	const [password, setPassword] = useState('');
	const navigate = useNavigate();

	const handleSubmit = async (e) => {
		e.preventDefault();
		try {   // 백엔드(API)로 username, password 보냄
			const response = await axios.post('/api/token/', {
        			username,
        			password,
			}, { headers: {Authorization: undefined } //기존 헤더 제거
			});
	
			// 토큰을 LocalStorage에 저장, 이후 요청시 헤더에 실어 보냄.
			localStorage.setItem('access', response.data.access);
			localStorage.setItem('refresh', response.data.refresh);

			console.log('succesfully login!');
			// 로그인 성공 후 메인 페이지로 이동
			navigate('/');
		} catch (error) {
			alert('로그인 실패! 아이디와 비밀번호를 확인해주세요.');
    		}  };

	return (
		<div>
		<h2>로그인</h2>
			<form onSubmit={handleSubmit}>
			<input
				type="text"
          			placeholder="username"
          			value={username}
          			onChange={(e) => setUsername(e.target.value)}
          			required
        		/>
        		<input
          			type="password"
          			placeholder="password"
          			value={password}
          			onChange={(e) => setPassword(e.target.value)}
          			required
        		/>
        		<button type="submit">로그인</button>
      			</form>
    		</div>
  	);
};

export default LoginPage;
