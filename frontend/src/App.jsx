import { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [usuario, setUsuario] = useState(null);

  const [login, setLogin] = useState({
    correo: "",
   password: ""
  });

  const [errorLogin, setErrorLogin] = useState("");

  
  const [estadisticas, setEstadisticas] = useState({
    total_alumnos: 0,
    total_asistencias: 0
  });

  const [alumnos, setAlumnos] = useState([]);
  const [asistencias, setAsistencias] = useState([]);
  const [grupos, setGrupos] = useState([]);

  const [grupoSeleccionado, setGrupoSeleccionado] = useState("");
  const [mensajeAsistencia, setMensajeAsistencia] = useState("");

  const [grupoActivo, setGrupoActivo] = useState(null);
  const [nombreGrupoActivo, setNombreGrupoActivo] = useState("");  

  const [asistenciasGrupo, setAsistenciasGrupo] = useState([]);
  const [grupoConsulta, setGrupoConsulta] = useState("");

  const [pantalla, setPantalla] = useState("dashboard");

  const [grupoAlumnosConsulta, setGrupoAlumnosConsulta] = useState("");
  const [alumnosGrupo, setAlumnosGrupo] = useState([]);

  const [formulario, setFormulario] = useState({
    nombre: "",
    matricula: "",
    grupo: "",
    grupo_id: ""
  });

  const [formGrupo, setFormGrupo] = useState({
    nombre: "",
    materia: "",
    aula: "",
    dias: [],
    hora_inicio: "",
    hora_fin: ""
  });

  const cargarDatos = () => {
    fetch("http://127.0.0.1:8000/estadisticas")
      .then(response => response.json())
      .then(data => setEstadisticas(data));

    fetch("http://127.0.0.1:8000/alumnos")
      .then(response => response.json())
      .then(data => setAlumnos(data));

    fetch("http://127.0.0.1:8000/asistencias")
      .then(response => response.json())
      .then(data => setAsistencias(data));

    fetch(`http://127.0.0.1:8000/maestros/${usuario.id}/grupos`)
      .then(response => response.json())
      .then(data => setGrupos(data));
    
    fetch("http://127.0.0.1:8000/grupo-activo")
      .then(response => response.json())
      .then(data => {
        setGrupoActivo(data.grupo_id);

        const grupoEncontrado = grupos.find(
          grupo => grupo.id === data.grupo_id
        );

        if (grupoEncontrado) {
          setNombreGrupoActivo(grupoEncontrado.nombre);
        } else {
          setNombreGrupoActivo("");
        }
      });
  };



useEffect(() => {
  if (usuario) {
    cargarDatos();
  }
}, [usuario]);

  const registrarAlumno = (e) => {
    e.preventDefault();

    fetch("http://127.0.0.1:8000/alumnos", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        ...formulario,
        grupo_id: Number(formulario.grupo_id)
      })
    })
      .then(response => response.json())
      .then(() => {
        setFormulario({
          nombre: "",
          matricula: "",
          grupo: "",
          grupo_id: ""
        });

        cargarDatos();
      });
  };

  const registrarGrupo = (e) => {
    e.preventDefault();

    fetch("http://127.0.0.1:8000/grupos", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        ...formGrupo,
        dias: formGrupo.dias.join(", "),
        maestro_id: usuario.id
      })
          })
      .then(response => response.json())
      .then(() => {
        setFormGrupo({
          nombre: "",
          materia: "",
          aula: "",
          hora_inicio: "",
          hora_fin: ""
        });

        cargarDatos();
      });
  };

  const iniciarAsistencia = (e) => {
    e.preventDefault();

    fetch("http://127.0.0.1:8000/iniciar-asistencia", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        grupo_id: Number(grupoSeleccionado)
      })
    })
      .then(response => response.json())
      .then(data => {
    setMensajeAsistencia(
      `Asistencia iniciada para grupo ${data.grupo_id}`
    );

    cargarDatos();
  });
  };
  
  const finalizarAsistencia = () => {

  fetch("http://127.0.0.1:8000/finalizar-asistencia", {
    method: "POST"
    })
    .then(response => response.json())
    .then(data => {
      setMensajeAsistencia(data.mensaje);
      setGrupoSeleccionado("");

      cargarDatos();
    });

  };

  const consultarAsistenciasGrupo = () => {

    if (!grupoConsulta) return;

    fetch(
      `http://127.0.0.1:8000/grupos/${grupoConsulta}/asistencias`
    )
     .then(response => response.json())
      .then(data => {
        setAsistenciasGrupo(data);
     });

  };

  const consultarAlumnosGrupo = () => {
    if (!grupoAlumnosConsulta) return;

    fetch(`http://127.0.0.1:8000/grupos/${grupoAlumnosConsulta}/alumnos`)
      .then(response => response.json())
      .then(data => {
        setAlumnosGrupo(data);
      });
  };

  const iniciarSesion = (e) => {
    e.preventDefault();

    fetch("http://127.0.0.1:8000/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(login)
    })
      .then(response => response.json())
      .then(data => {
        if (data.acceso) {
          setUsuario(data.maestro);
          setErrorLogin("");
          cargarDatos();
        } else {
          setErrorLogin("Correo o contraseña incorrectos");
        }
      });
  };

  if (!usuario) {
    return (
      <div className="contenedor">
        <div className="seccion">
          <h1 className="titulo">Login Maestro</h1>

          <form className="formulario" onSubmit={iniciarSesion}>
            <input
              type="email"
              placeholder="Correo"
              value={login.correo}
              onChange={(e) =>
                setLogin({ ...login, correo: e.target.value })
              }
            />

            <input
              type="password"
              placeholder="Contraseña"
              value={login.password}
              onChange={(e) =>
                setLogin({ ...login, password: e.target.value })
              }
            />

            <button type="submit">
              Iniciar sesión
            </button>
          </form>

          <p>{errorLogin}</p>
        </div>
      </div>
    );
  }


  return (
    <div className="app-layout">

      <aside className="sidebar">
        <h2>Asistencia Facial</h2>

        <button onClick={() => setPantalla("dashboard")}>📊 Dashboard</button>
        <button onClick={() => setPantalla("grupos")}> 👥 Grupos</button>
        <button onClick={() => setPantalla("alumnos")}>🎓 Alumnos</button>
        <button onClick={() => setPantalla("asistencia")}>📷 Tomar asistencia</button>
        <button onClick={() => setPantalla("reportes")}>📋 Reportes</button>

        <button className="logout" onClick={() => setUsuario(null)}>
          Cerrar sesión
        </button>
      </aside>

    <main className="contenido">

      <h1 className="titulo">Sistema de Asistencia Facial</h1>
      <p>
        Sesión iniciada como: <strong>{usuario.nombre}</strong>
      </p>
      
      {pantalla === "dashboard" && (
        <>
        <div className="tarjetas">
          <div className="tarjeta">
            <h3>Total alumnos</h3>
            <p>{estadisticas.total_alumnos}</p>
          </div>

          <div className="tarjeta">
            <h3>Total asistencias</h3>
            <p>{estadisticas.total_asistencias}</p>
          </div>

          <div className="tarjeta">
            <h3>Total grupos</h3>
            <p>{grupos.length}</p>
          </div>
        </div>
        </>
      )}

      {pantalla === "grupos" && (
        <>
        <div className="seccion">
          <h2>Crear grupo</h2>

          <form className="formulario" onSubmit={registrarGrupo}>
            <input
              type="text"
              placeholder="Grupo"
              value={formGrupo.nombre}
              onChange={(e) =>
                setFormGrupo({ ...formGrupo, nombre: e.target.value })
              }
            />

            <input
              type="text"
              placeholder="Materia"
              value={formGrupo.materia}
              onChange={(e) =>
                setFormGrupo({ ...formGrupo, materia: e.target.value })
              }
            />

            <input
              type="text"
              placeholder="Aula"
              value={formGrupo.aula}
              onChange={(e) =>
                setFormGrupo({ ...formGrupo, aula: e.target.value })
              }
            />
            <h3>Días de clase</h3>

            <label>
              <input
                type="checkbox"
                value="Lunes"
                onChange={(e) => {
                  if (e.target.checked) {
                    setFormGrupo({
                      ...formGrupo,
                      dias: [...formGrupo.dias, "Lunes"]
                    });
                  } else {
                    setFormGrupo({
                      ...formGrupo,
                      dias: formGrupo.dias.filter(
                        dia => dia !== "Lunes"
                      )
                    });
                  }
                }}
              />
              Lunes
            </label>

            <label>
              <input
                type="checkbox"
                value="Martes"
                onChange={(e) => {
                  if (e.target.checked) {
                    setFormGrupo({
                      ...formGrupo,
                      dias: [...formGrupo.dias, "Martes"]
                    });
                  } else {
                    setFormGrupo({
                      ...formGrupo,
                      dias: formGrupo.dias.filter(
                        dia => dia !== "Martes"
                      )
                    });
                  }
                }}
              />
              Martes
            </label>

            <label>
              <input
                type="checkbox"
                value="Miércoles"
                onChange={(e) => {
                  if (e.target.checked) {
                    setFormGrupo({
                      ...formGrupo,
                      dias: [...formGrupo.dias, "Miércoles"]
                    });
                  } else {
                    setFormGrupo({
                      ...formGrupo,
                      dias: formGrupo.dias.filter(
                        dia => dia !== "Miércoles"
                      )
                    });
                  }
                }}
              />
              Miércoles
            </label>

            <label>
              <input
                type="checkbox"
                value="Jueves"
                onChange={(e) => {
                  if (e.target.checked) {
                    setFormGrupo({
                      ...formGrupo,
                      dias: [...formGrupo.dias, "Jueves"]
                    });
                  } else {
                    setFormGrupo({
                      ...formGrupo,
                      dias: formGrupo.dias.filter(
                        dia => dia !== "Jueves"
                      )
                    });
                  }
                }}
              />
              Jueves
            </label>

            <label>
              <input
                type="checkbox"
                value="Viernes"
                onChange={(e) => {
                  if (e.target.checked) {
                    setFormGrupo({
                      ...formGrupo,
                      dias: [...formGrupo.dias, "Viernes"]
                    });
                  } else {
                    setFormGrupo({
                      ...formGrupo,
                      dias: formGrupo.dias.filter(
                        dia => dia !== "Viernes"
                      )
                    });
                  }
                }}
              />
              Viernes
            </label>

            <label>
              <input
                type="checkbox"
                value="Sabado"
                onChange={(e) => {
                  if (e.target.checked) {
                    setFormGrupo({
                      ...formGrupo,
                      dias: [...formGrupo.dias, "Sabado"]
                    });
                  } else {
                    setFormGrupo({
                      ...formGrupo,
                      dias: formGrupo.dias.filter(
                        dia => dia !== "Sabado"
                      )
                    });
                  }
                }}
              />
              Sabado
            </label>

            <input
              type="time"
              placeholder="Hora inicio"
              value={formGrupo.hora_inicio}
              onChange={(e) =>
                setFormGrupo({ ...formGrupo, hora_inicio: e.target.value })
              }
            />


            <input
              type="time"
              placeholder="Hora fin"
              value={formGrupo.hora_fin}
              onChange={(e) =>
                setFormGrupo({ ...formGrupo, hora_fin: e.target.value })
              }
            />

            <button type="submit">Guardar grupo</button>
          </form>
        </div>
        
      

        <div className="seccion">
          <h2>Grupos registrados</h2>

          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Materia</th>
                <th>Grupo</th>
                <th>Aula</th>
                <th>Días</th>
                <th>Hora inicio</th>
                <th>Hora fin</th>
              </tr>
            </thead>

            <tbody>
              {grupos.map(grupo => (
                <tr key={grupo.id}>
                  <td>{grupo.id}</td>
                  <td>{grupo.materia}</td>
                  <td>{grupo.nombre}</td>
                  <td>{grupo.aula}</td>
                  <td>{grupo.dias}</td>
                  <td>{grupo.hora_inicio}</td>
                  <td>{grupo.hora_fin}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        </>
      )}

      {pantalla === "alumnos" && (
        <>

        <div className="seccion">
          <h2>Registrar alumno</h2>

          <form className="formulario" onSubmit={registrarAlumno}>
            <input
              type="text"
              placeholder="Nombre"
              value={formulario.nombre}
              onChange={(e) =>
                setFormulario({ ...formulario, nombre: e.target.value })
              }
            />

            <input
              type="text"
              placeholder="Matrícula"
              value={formulario.matricula}
              onChange={(e) =>
                setFormulario({ ...formulario, matricula: e.target.value })
              }
            />

            <select
              value={formulario.grupo_id}
              onChange={(e) => {
                const grupoSeleccionado = grupos.find(
                  grupo => grupo.id === Number(e.target.value)
                );

                setFormulario({
                  ...formulario,
                  grupo_id: e.target.value,
                  grupo: grupoSeleccionado ? grupoSeleccionado.nombre : ""
                });
              }}
            >
              <option value="">Selecciona un grupo</option>

              {grupos.map(grupo => (
                <option key={grupo.id} value={grupo.id}>
                  {grupo.nombre}
                </option>
              ))}
            </select>

            <button type="submit">Guardar alumno</button>
          </form>
        </div>

        <div className="seccion">
          <h2>Consultar alumnos por grupo</h2>

          <select
            value={grupoAlumnosConsulta}
            onChange={(e) => setGrupoAlumnosConsulta(e.target.value)}
          >
            <option value="">Selecciona un grupo</option>

            {grupos.map(grupo => (
              <option key={grupo.id} value={grupo.id}>
                {grupo.materia} - {grupo.nombre}
              </option>
            ))}
          </select>

          <button onClick={consultarAlumnosGrupo}>
            Consultar
          </button>

          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Nombre</th>
                <th>Matrícula</th>
                <th>Grupo</th>
              </tr>
            </thead>

            <tbody>
              {alumnosGrupo.map(alumno => (
                <tr key={alumno.id}>
                  <td>{alumno.id}</td>
                  <td>{alumno.nombre}</td>
                  <td>{alumno.matricula}</td>
                  <td>{alumno.grupo}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="seccion">
          <h2>Alumnos registrados</h2>

          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Nombre</th>
                <th>Matrícula</th>
                <th>Grupo</th>
              </tr>
            </thead>

            <tbody>
              {alumnos.map(alumno => (
                <tr key={alumno.id}>
                  <td>{alumno.id}</td>
                  <td>{alumno.nombre}</td>
                  <td>{alumno.matricula}</td>
                  <td>{alumno.nombre_grupo || alumno.grupo}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        </>
      )}

      {pantalla === "asistencia" && (
        <>
        <div className="seccion">
          <h2>Estado de asistencia</h2>

          {grupoActivo ? (
          <p>
            🟢 Asistencia activa para el grupo:
            {" "}
            <strong>
              {nombreGrupoActivo || grupoActivo}
            </strong>
          </p>
          ) : (
          <p>
            🔴 No hay asistencia activa
          </p>
          )}
        </div>

        <div className="seccion">
          <h2>Tomar asistencia</h2>

          <form className="formulario" onSubmit={iniciarAsistencia}>
            <select
              value={grupoSeleccionado}
              onChange={(e) => setGrupoSeleccionado(e.target.value)}
            >
              <option value="">Selecciona un grupo</option>

              {grupos.map(grupo => (
                <option key={grupo.id} value={grupo.id}>
                  {grupo.nombre}
                </option>
              ))}
            </select>

            <button type="submit">Iniciar asistencia</button>
            <button type="button" onClick={finalizarAsistencia}>Finalizar asistencia</button>
          </form>

          <p>{mensajeAsistencia}</p>
        </div>

        
         </>
      )}

      {pantalla === "reportes" && (
        <>

        <div className="seccion">

          <h2>Asistencias por grupo</h2>

          <select
            value={grupoConsulta}
            onChange={(e) => setGrupoConsulta(e.target.value)}
          >

            <option value="">
              Selecciona un grupo
            </option>

            {grupos.map(grupo => (
              <option
                key={grupo.id}
                value={grupo.id}
              >
                {grupo.nombre}
              </option>
            ))}

          </select>

          <button
            onClick={consultarAsistenciasGrupo}
          >
            Consultar
          </button>

          <table>
            <thead>
              <tr>
                <th>Alumno</th>
                <th>Matrícula</th>
                <th>Fecha</th>
                <th>Hora</th>
              </tr>
            </thead>

            <tbody>

              {asistenciasGrupo.map(asistencia => (

              <tr key={asistencia.id}>

                  <td>{asistencia.nombre}</td>

                <td>{asistencia.matricula}</td>

                  <td>{asistencia.fecha}</td>

                  <td>{asistencia.hora}</td>

                </tr>

            ))}

          </tbody>

          </table>

        </div>


        <div className="seccion">
          <h2>Historial de asistencias</h2>

          <table>
            <thead>
              <tr>
                <th>Alumno</th>
                <th>Fecha</th>
                <th>Hora</th>
              </tr>
            </thead>

            <tbody>
              {asistencias.map(asistencia => (
                <tr key={asistencia.id}>
                  <td>{asistencia.nombre}</td>
                  <td>{asistencia.fecha}</td>
                  <td>{asistencia.hora}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        </>
      )}
      </main>
    </div>
  );
}

export default App;