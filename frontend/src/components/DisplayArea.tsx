import React from 'react';
import { TextField } from '@mui/material';
interface DisplayProps {
    text: string;
    visibility: boolean;
}

const Display: React.FC<DisplayProps> = ({ text, visibility }) => {
    return (
        <TextField
            value={text}
            multiline
            fullWidth
            minRows={4}
            style={{ color:'white', marginTop: '10px', visibility: visibility? 'visible': 'hidden'}}
            variant="outlined"
            InputProps={{
                readOnly: true,
                style: { color: 'white' }
            }}
        />
    );
};

export default Display;