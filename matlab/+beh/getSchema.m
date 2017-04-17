function obj = getSchema
persistent schemaObject
if isempty(schemaObject)
    schemaObject = dj.Schema(dj.conn, 'beh', 'pipeline_behavior');
end
obj = schemaObject;
end