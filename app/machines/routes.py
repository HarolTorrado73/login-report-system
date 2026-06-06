from flask import Blueprint, render_template, request, jsonify

from app.services.machines import get_machine_stats, filter_machines

machines = Blueprint("machines", __name__)


@machines.route("/machines")
def machines_page():
    machine_list = get_machine_stats()
    filtered = filter_machines(
        machine_list,
        status=request.args.get("status"),
        os_filter=request.args.get("os"),
        search=request.args.get("q"),
    )
    statuses = sorted({m["status"] for m in machine_list})
    oss = sorted({m["os"] for m in machine_list})
    return render_template(
        "machines.html",
        machines=filtered,
        all_machines=machine_list,
        statuses=statuses,
        oss=oss,
        view=request.args.get("view", "grid"),
        q=request.args.get("q", ""),
    )


@machines.route("/machines/data")
def machines_data():
    machine_list = get_machine_stats()
    filtered = filter_machines(
        machine_list,
        status=request.args.get("status"),
        os_filter=request.args.get("os"),
        search=request.args.get("q"),
    )
    return jsonify({"machines": filtered, "total": len(filtered)})
