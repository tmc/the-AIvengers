pip install -r requirements.txt
uvicorn api:app --reload

curl -X POST "http://127.0.0.1:8000/write_code/" -H "Content-Type: application/json" -d '{
  "input_prompt": "1. Visualize these images in row by row, max width is 500px: \n- https://images.unsplash.com/photo-1682685796965-9814afcbff55\n- https://images.unsplash.com/photo-1661956601349-f61c959a8fd4\n2. Add title \"AIvenger demo show\"\n3. Write \"Hello world\" as body texts\n4. Add a button \"Click me\" at the bottom, when click, it will hide/unhide all images",
  "out_file": "output.js"
}'