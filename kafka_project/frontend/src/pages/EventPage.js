import React, {useEffect, useState} from "react";
import axios from "axios";

function EventPage(){
	const [events, setEvents] = useState([]);

	useEffect(() => {
		axios
			.get("/api/events/")
			.then((res) => {
		    		console.log(res.data);
				setEvents(res.data);
		    	})
			.catch((err) => {
				console.error(err);
			});
	}, []);

	return (
		<div>
			<h1> Event List </h1>
			<ul>
		    		{events.map((event) => (
				<li key={event.id}>
			    	<strong>{event.title}</strong> ({event.start_date} ~ {event.end_date})
				</li>
		    		))}
			</ul>
	    </div>
	);
}

export default EventPage;
