import os
import tempfile
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from parser import parse_pdf, fastpass_info, is_fastpass_worth_it
app = Flask(__name__)
CORS(app)

@app.route('/api/parse', methods=['POST'])
def process_pdf():
    # Check if the request has a file
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    # If user does not select file, browser might send empty file
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Check if the file is a PDF
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'File must be a PDF'}), 400
    
    # Save the file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
        file.save(temp_file.name)
        pdf_path = temp_file.name
    
    try:
        # Process the PDF
        df, error = parse_pdf(pdf_path)
        
        if error:
            return jsonify({'error': error}), 500
        
        # Convert DataFrame to JSON for the response
        transactions = df.to_dict('records')
        
        # Get fastpass info if requested
        calculate_fastpass = request.form.get('fastpass', 'false').lower() in ['true', 't', '1', 'yes']
        fastpass_results = {}
        
        if calculate_fastpass:
            fastpass_results = fastpass_info(df)
        
        calculate_is_worth_it = request.form.get('worth', 'false').lower() in ['true', 't', '1', 'yes']
        
        if calculate_is_worth_it:
            is_worth_results = is_fastpass_worth_it(df)

        # Remove the temporary file
        os.unlink(pdf_path)
        
        # Return the results
        return jsonify({
            'transactions': transactions,
            'fastpass_info': fastpass_results if calculate_fastpass else None,
            'is_worth_it': is_worth_results if calculate_is_worth_it else None
        })
    
    except Exception as e:
        # Clean up the temporary file
        logging.exception("Exception occurred")
        if os.path.exists(pdf_path):
            os.unlink(pdf_path)
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    # Use environment variables for configuration in production
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)