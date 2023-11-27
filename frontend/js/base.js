// Script necessary for every page

// Do not hardcode request URL in js file.
// A example for API: /scores/basic_info/by_class/<int:class_id>/exam/<int:exam_id>
// url = `${protocolPrefix}${host}/api/scores/basic_info/by_class/${class_id}/exam/${exam_id}`;
// fetch(url).then(() => {...});
const protocolPrefix = window.location.protocol + "//";
const host = window.location.host;

