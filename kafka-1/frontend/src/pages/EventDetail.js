import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

function EventDetail() {
	const { id } = useParams();
	const [event, setEvent] = useState(null);
	const [message, setMessage] = useState('');

  	useEffect(() => {
    		axios.get(`/api/events/${id}/`)
      		.then(res => setEvent(res.data))
      		.catch(err => console.error(err));
  	}, [id]);

  	const handleIssueCoupon = () => {
		const token = localStorage.getItem('access') // JWT 액세스 토큰
    		console.log(token);
		console.log(typeof id);
		axios.post(`/api/coupon-issue/`, 
			{ event_id: id },
			{
				headers: {
					Authorization: `Bearer ${token}`
				}
			}
		)
      		.then(res => setMessage('쿠폰이 발급되었습니다!'))
      		.catch(err => {
        		console.error(err);
        		setMessage('쿠폰 발급 실패');
      		});
  	};

  	if (!event) return <div>Loading...</div>;

	return (
    		<div>
      			<h2>{event.title}</h2>
	      		<p>{event.description}</p>
      			<p>시작일: {event.start_date}</p>
      			<p>종료일: {event.end_date}</p>
      			<button onClick={handleIssueCoupon}>쿠폰 발급받기</button>
      			{message && <p>{message}</p>}
    		</div>
  	);
}

export default EventDetail;
