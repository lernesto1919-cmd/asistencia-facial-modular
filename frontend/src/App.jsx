import { useState, useEffect, useRef } from "react";
import "./App.css";

function App() {
  const [usuario, setUsuario] = useState(null);

  const [login, setLogin] = useState({
    correo: "",
   password: ""
  });
  const [errorLogin, setErrorLogin] = useState("");
  const [modoRegistro, setModoRegistro] = useState(false);

  const [registroMaestro, setRegistroMaestro] = useState({
    nombre: "",
    correo: "",
    password: "",
    confirmarPassword: ""
  });

  const [tipoAcceso, setTipoAcceso] = useState("maestro");

  const [accesoAlumno, setAccesoAlumno] = useState({
    matricula: "",
    codigo: ""
  });


  const [mensajeAlumno, setMensajeAlumno] = useState("");

  const [alumnoActual, setAlumnoActual] = useState(null);

  const [mensajeRegistro, setMensajeRegistro] = useState("");

  const [mostrarCamara, setMostrarCamara] = useState(false);

  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [fotoCapturada, setFotoCapturada] = useState(null);

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

  const [busquedaAlumno, setBusquedaAlumno] = useState("");
  const [resultadoBusqueda, setResultadoBusqueda] = useState([]);

  const [registrandoRostro, setRegistrandoRostro] = useState(null);
  const [rostroRegistrado, setRostroRegistrado] = useState(null);

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

  const cargarDatos = (maestroId = usuario?.id) => {
    if (!maestroId) return;

    fetch(`http://192.168.50.209:8000/maestros/${maestroId}/estadisticas`)
      .then(response => response.json())
      .then(data => setEstadisticas(data));

    fetch(`http://192.168.50.209:8000/maestros/${maestroId}/alumnos`)
      .then(response => response.json())
      .then(data => setAlumnos(data));

    fetch(`http://192.168.50.209:8000/maestros/${maestroId}/asistencias`)
      .then(response => response.json())
      .then(data => setAsistencias(data));

    fetch(`http://192.168.50.209:8000/maestros/${maestroId}/grupos`)
      .then(response => response.json())
      .then(data => {
        setGrupos(data);

        fetch("http://192.168.50.209:8000/grupo-activo")
          .then(response => response.json())
          .then(activo => {
            setGrupoActivo(activo.grupo_id);

            const grupoEncontrado = data.find(
              grupo => grupo.id === activo.grupo_id
            );

            if (grupoEncontrado) {
              setNombreGrupoActivo(grupoEncontrado.nombre);
            } else {
              setNombreGrupoActivo("");
            }
          });
      });
  };



useEffect(() => {
  if (usuario) {
    cargarDatos();
  }
}, [usuario]);

  const registrarAlumno = (e) => {
    e.preventDefault();

    fetch("http://192.168.50.209:8000/alumnos", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        ...formulario,
        grupo_id: Number(formulario.grupo_id),
        maestro_id: usuario.id
      })
    })
      .then(response => response.json())
      .then(data => {
        if (data.ok === false) {
          alert(data.mensaje);
          return;
        }

        setFormulario({
          nombre: "",
          matricula: "",
          grupo: "",
          grupo_id: ""
        });

        cargarDatos(usuario.id);
      })
      .catch(error => {
        console.error(error);
        alert("No se pudo registrar el alumno");
      });
  };

  const registrarGrupo = (e) => {
    e.preventDefault();

    fetch("http://192.168.50.209:8000/grupos", {
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
      .then(data => {
        if (data.ok === false) {
          alert(data.mensaje);
          return;
        }

        setFormGrupo({
          nombre: "",
          materia: "",
          aula: "",
          dias: [],
          hora_inicio: "",
          hora_fin: ""
        });

        cargarDatos(usuario.id);
      })
      .catch(error => {
        console.error(error);
        alert("No se pudo registrar el grupo");
      });
  };

  const eliminarGrupo = async (grupo) => {
    const confirmar = window.confirm(
      `¿Seguro que deseas eliminar el grupo ${grupo.nombre}?`
    );

    if (!confirmar) {
      return;
    }

    try {
      const response = await fetch(
        `http://192.168.50.209:8000/grupos/${grupo.id}`,
        {
          method: "DELETE"
        }
      );

      const data = await response.json();

      if (data.ok) {
        alert(data.mensaje);
        cargarDatos();
      } else {
        alert(data.mensaje);
      }

    } catch (error) {
      console.error(error);
      alert("No se pudo eliminar el grupo");
    }
  };

  const iniciarAsistencia = (e) => {
    e.preventDefault();

    fetch("http://192.168.50.209:8000/iniciar-asistencia", {
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

  fetch("http://192.168.50.209:8000/finalizar-asistencia", {
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
      `http://192.168.50.209:8000/grupos/${grupoConsulta}/asistencias`
    )
     .then(response => response.json())
      .then(data => {
        setAsistenciasGrupo(data);
     });

  };

  const consultarAlumnosGrupo = () => {
    if (!grupoAlumnosConsulta) return;

    fetch(`http://192.168.50.209:8000/grupos/${grupoAlumnosConsulta}/alumnos`)
      .then(response => response.json())
      .then(data => {
        setAlumnosGrupo(data);
      });
  };

  const iniciarSesion = (e) => {
    e.preventDefault();

    fetch("http://192.168.50.209:8000/login", {
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
          cargarDatos(data.maestro.id);
        } else {
          setErrorLogin("Correo o contraseña incorrectos");
        }
      });
  };
  const registrarMaestro = (e) => {
    e.preventDefault();

    if (
      !registroMaestro.nombre ||
      !registroMaestro.correo ||
      !registroMaestro.password ||
      !registroMaestro.confirmarPassword
    ) {
      setMensajeRegistro("Completa todos los campos");
      return;
    }

    if (registroMaestro.password !== registroMaestro.confirmarPassword) {
      setMensajeRegistro("Las contraseñas no coinciden");
      return;
    }

    fetch("http://192.168.50.209:8000/maestros", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        nombre: registroMaestro.nombre,
        correo: registroMaestro.correo,
        password: registroMaestro.password
      })
    })
      .then(response => response.json())
      .then(data => {
        if (data.ok) {
          setMensajeRegistro("");
          setRegistroMaestro({
            nombre: "",
            correo: "",
            password: "",
            confirmarPassword: ""
          });

          setLogin({
            correo: registroMaestro.correo,
            password: ""
          });

          setModoRegistro(false);
          alert("Cuenta creada correctamente. Ahora inicia sesión.");
        } else {
          setMensajeRegistro(data.mensaje);
        }
      })
      .catch(error => {
        console.error(error);
        setMensajeRegistro("No se pudo crear la cuenta");
      });
  };

  const unirseClase = (e) => {
    e.preventDefault();

    setMensajeAlumno("");

    fetch("http://192.168.50.209:8000/alumnos/unirse-clase", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        matricula: accesoAlumno.matricula,
        codigo: accesoAlumno.codigo
      })
    })
      .then(response => response.json())
      .then(data => {
        if (data.ok) {
          setAlumnoActual(data.alumno);

          setMensajeAlumno(
            `Te uniste correctamente a ${data.grupo.materia} - ${data.grupo.nombre}`
          );

          setAccesoAlumno({
            matricula: "",
            codigo: ""
          });
        } else {
          setMensajeAlumno(data.mensaje);
        }
      })
      .catch(error => {
        console.error(error);
        setMensajeAlumno("No se pudo conectar con el servidor");
      });
  };

  const buscarAlumno = () => {

    const resultado = alumnos.filter(alumno =>
      alumno.nombre
        .toLowerCase()
        .includes(busquedaAlumno.toLowerCase())
      ||
      alumno.matricula
        .toString()
        .includes(busquedaAlumno)
    );
    setResultadoBusqueda(resultado);

  };


const registrarRostro = (alumno) => {

  setRegistrandoRostro(alumno.id);
  setRostroRegistrado(null);

  fetch(
    `http://192.168.50.209:8000/alumnos/${alumno.id}/registrar-rostro-maestro`,
    {
      method: "POST"
    }
  )
    .then(response => response.json())
    .then(data => {

      if (data.ok) {

        setRegistrandoRostro(null);
        setRostroRegistrado(alumno.id);

        // Actualizar el alumno en la tabla
        setAlumnos(alumnosActuales =>
          alumnosActuales.map(item =>
            item.id === alumno.id
              ? { ...item, rostro_registrado: 1 }
              : item
          )
        );

      } else {

        setRegistrandoRostro(null);

        alert(data.mensaje);

      }

    })
    .catch(() => {

      setRegistrandoRostro(null);

      alert("No se pudo iniciar la cámara.");

    });

};

const abrirCamaraAlumno = async () => {
  if (!alumnoActual) {
    setMensajeAlumno("No se encontró el alumno");
    return;
  }

  try {
    setMensajeAlumno("Preparando registro facial...");

    // Limpiar las fotografías anteriores
    const response = await fetch(
      `http://192.168.50.209:8000/alumnos/${alumnoActual.id}/preparar-registro-rostro`,
      {
        method: "POST"
      }
    );

    const data = await response.json();

    if (!data.ok) {
      setMensajeAlumno(data.mensaje);
      return;
    }

    // Abrir cámara
    const stream = await navigator.mediaDevices.getUserMedia({
      video: {
        facingMode: "user"
      },
      audio: false
    });

    setMostrarCamara(true);
    setFotoCapturada(null);
    setMensajeAlumno("");

    setTimeout(() => {
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      }
    }, 100);

  } catch (error) {
    console.error(error);
    setMensajeAlumno("No se pudo iniciar el registro facial");
  }
};

const capturarFoto = () => {
  const video = videoRef.current;
  const canvas = canvasRef.current;

  if (!video || !canvas) return;

  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;

  const contexto = canvas.getContext("2d");

  contexto.drawImage(
    video,
    0,
    0,
    canvas.width,
    canvas.height
  );

  const imagen = canvas.toDataURL("image/jpeg", 0.9);

  setFotoCapturada(imagen);
};

const enviarFoto = () => {
  if (!fotoCapturada || !alumnoActual) {
    setMensajeAlumno("Primero toma una foto");
    return;
  }

  fetch(
    `http://192.168.50.209:8000/alumnos/${alumnoActual.id}/subir-rostro`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        imagen: fotoCapturada
      })
    }
  )
    .then(response => response.json())
    .then(data => {
      if (data.ok) {
        setMensajeAlumno(
          `✅ Foto ${data.numero} guardada correctamente`
        );
      } else {
        setMensajeAlumno(data.mensaje);
      }
    })
    .catch(error => {
      console.error(error);
      setMensajeAlumno("No se pudo enviar la fotografía");
    });
};

const registrarRostroAutomatico = async () => {
  const video = videoRef.current;
  const canvas = canvasRef.current;

  if (!video || !canvas || !alumnoActual) {
    setMensajeAlumno("No se pudo iniciar el registro facial");
    return;
  }

  setMensajeAlumno("📷 Iniciando registro facial...");

  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;

  const contexto = canvas.getContext("2d");

  for (let i = 1; i <= 30; i++) {
    contexto.drawImage(
      video,
      0,
      0,
      canvas.width,
      canvas.height
    );

    const imagen = canvas.toDataURL("image/jpeg", 0.9);

    try {
      const response = await fetch(
        `http://192.168.50.209:8000/alumnos/${alumnoActual.id}/subir-rostro`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            imagen: imagen
          })
        }
      );

      const data = await response.json();

      if (!data.ok) {
        setMensajeAlumno(`❌ Error en la foto ${i}`);
        return;
      }

      setMensajeAlumno(
        `📸 Capturando rostro... ${i}/30`
      );

    } catch (error) {
      console.error(error);
      setMensajeAlumno("❌ Error al enviar las fotografías");
      return;
    }

    await new Promise(resolve => setTimeout(resolve, 500));
  }

  setMensajeAlumno("🧠 Entrenando reconocimiento facial...");

  try {
    const response = await fetch(
      `http://192.168.50.209:8000/alumnos/${alumnoActual.id}/registrar-rostro`,
      {
        method: "POST"
      }
    );

    const data = await response.json();

    if (data.ok) {

      if (videoRef.current?.srcObject) {
        const stream = videoRef.current.srcObject;

        stream.getTracks().forEach(track => {
          track.stop();
        });

        videoRef.current.srcObject = null;
      }

      setMostrarCamara(false);
      setFotoCapturada(null);

      setAlumnoActual({
        ...alumnoActual,
        rostro_registrado: 1
      });

      setMensajeAlumno(
        `✅ Rostro registrado correctamente (${data.imagenes} imágenes)`
      );
    } else {
      setMensajeAlumno(
        `❌ ${data.mensaje}`
      );
    }

  } catch (error) {
    console.error(error);

    setMensajeAlumno(
      "❌ No se pudo entrenar el reconocimiento facial"
    );
  }
};

const eliminarAlumno = async (alumno) => {
  const confirmar = window.confirm(
    `¿Seguro que deseas eliminar a ${alumno.nombre}?`
  );

  if (!confirmar) {
    return;
  }

  try {
    const response = await fetch(
      `http://192.168.50.209:8000/alumnos/${alumno.id}`,
      {
        method: "DELETE"
      }
    );

    const data = await response.json();

    if (data.ok) {
      alert(data.mensaje);
      cargarDatos();
    } else {
      alert(data.mensaje);
    }

  } catch (error) {
    console.error(error);
    alert("No se pudo eliminar el alumno");
  }

};



  if (!usuario) {
    return (
      <div className="contenedor">
        <div className="seccion">
          <div className="selector-acceso">
            <button
              type="button"
              onClick={() => {
                setTipoAcceso("maestro");
                setMensajeAlumno("");
              }}
            >
              👨‍🏫 Maestro
            </button>

            <button
              type="button"
              onClick={() => {
                setTipoAcceso("alumno");
                setErrorLogin("");
                setModoRegistro(false);
              }}
            >
              🎓 Alumno
            </button>
          </div>

          {tipoAcceso === "alumno" ? (
            <>
              <h1 className="titulo">Portal del alumno</h1>

              {!alumnoActual ? (
                <>
                  <p>
                    Ingresa tu código de alumno y el código proporcionado por tu profesor.
                  </p>

                  <form className="formulario" onSubmit={unirseClase}>
                    <input
                      type="text"
                      placeholder="Código de alumno"
                      value={accesoAlumno.matricula}
                      onChange={(e) =>
                        setAccesoAlumno({
                          ...accesoAlumno,
                          matricula: e.target.value
                        })
                      }
                    />

                    <input
                      type="text"
                      placeholder="Código de clase"
                      value={accesoAlumno.codigo}
                      onChange={(e) =>
                        setAccesoAlumno({
                          ...accesoAlumno,
                          codigo: e.target.value.toUpperCase()
                        })
                      }
                    />

                    <button type="submit">
                      Unirme a la clase
                    </button>
                  </form>

                  <p>{mensajeAlumno}</p>
                </>
              ) : (
                <>
                  <h2>Hola, {alumnoActual.nombre}</h2>

                  <p>
                    Código de alumno: {alumnoActual.matricula}
                  </p>

                  <p>✅ Clase vinculada correctamente</p>

                  <button
                    type="button"
                    onClick={abrirCamaraAlumno}
                  >
                    📷 Registrar mi rostro
                  </button>
                  {mostrarCamara && (
                    <div>
                      <h3>Registro facial</h3>

                      <p>
                        Coloca tu rostro frente a la cámara.
                      </p>

                      <video
                        ref={videoRef}
                        autoPlay
                        playsInline
                        style={{
                          width: "100%",
                          maxWidth: "500px",
                          borderRadius: "10px"
                        }}
                      />
                      <button
                        type="button"
                        onClick={registrarRostroAutomatico}
                      >
                        📸 Iniciar captura automática
                      </button>
                      <canvas
                        ref={canvasRef}
                        style={{ display: "none" }}
                      />
                      
                      <p>{mensajeAlumno}</p>
                    </div>
                  )}
                </>
              )}
            </>
          ) : !modoRegistro ? (
            <>
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

              <p>¿No tienes una cuenta?</p>

              <button
                type="button"
                onClick={() => {
                  setModoRegistro(true);
                  setErrorLogin("");
                }}
              >
                Crear cuenta
              </button>
            </>
          ) : (
            <>
              <h1 className="titulo">Crear cuenta</h1>

              <form className="formulario" onSubmit={registrarMaestro}>
                <input
                  type="text"
                  placeholder="Nombre completo"
                  value={registroMaestro.nombre}
                  onChange={(e) =>
                    setRegistroMaestro({
                      ...registroMaestro,
                      nombre: e.target.value
                    })
                  }
                />

                <input
                  type="email"
                  placeholder="Correo"
                  value={registroMaestro.correo}
                  onChange={(e) =>
                    setRegistroMaestro({
                      ...registroMaestro,
                      correo: e.target.value
                    })
                  }
                />

                <input
                  type="password"
                  placeholder="Contraseña"
                  value={registroMaestro.password}
                  onChange={(e) =>
                    setRegistroMaestro({
                      ...registroMaestro,
                      password: e.target.value
                    })
                  }
                />

                <input
                  type="password"
                  placeholder="Confirmar contraseña"
                  value={registroMaestro.confirmarPassword}
                  onChange={(e) =>
                    setRegistroMaestro({
                      ...registroMaestro,
                      confirmarPassword: e.target.value
                    })
                  }
                />

                <button type="submit">
                  Crear cuenta
                </button>
              </form>

              <p>{mensajeRegistro}</p>

              <p>¿Ya tienes una cuenta?</p>

              <button
                type="button"
                onClick={() => {
                  setModoRegistro(false);
                  setMensajeRegistro("");
                }}
              >
                Volver al inicio de sesión
              </button>
            </>
          )}

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
                <th>Código de clase</th>
                <th>Acciones</th>
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
                  <td><strong>{grupo.codigo}</strong></td>

                  <td>
                    <button
                      type="button"
                      onClick={() => eliminarGrupo(grupo)}
                    >
                      🗑️ Eliminar
                    </button>
                  </td>
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

          <h2>Buscar alumno</h2>

          <input
            type="text"
            placeholder="Código o Nombre"
            value={busquedaAlumno}
            onChange={(e) =>
              setBusquedaAlumno(e.target.value)
            }
          />

          <button onClick={buscarAlumno}>
            Buscar
          </button>

          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Nombre</th>
                <th>Matrícula</th>
                <th>Grupo</th>
                <th>Rostro</th>
              </tr>
            </thead>

            <tbody>
              {resultadoBusqueda.map(alumno => (
                <tr key={alumno.id}>
                  <td>{alumno.id}</td>
                  <td>{alumno.nombre}</td>
                  <td>{alumno.matricula}</td>
                  <td>{alumno.nombre_grupo || alumno.grupo}</td>
                  <td>{alumno.rostro_registrado === 1
                      ? "✅ Registrado"
                      : "❌ No registrado"}</td>
                </tr>
              ))}
            </tbody>
          </table>

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

                  <td>
                    <button
                      type="button"
                      disabled={
                        registrandoRostro === alumno.id ||
                        alumno.rostro_registrado === 1 ||
                        rostroRegistrado === alumno.id
                      }
                      onClick={() => registrarRostro(alumno)}
                    >
                      {registrandoRostro === alumno.id
                        ? "⏳ Registrando..."
                        : alumno.rostro_registrado === 1 ||
                          rostroRegistrado === alumno.id
                        ? "✅ Rostro registrado"
                        : "📷 Registrar rostro"}
                    </button>

                    <button
                      type="button"
                      onClick={() => eliminarAlumno(alumno)}
                    >
                      🗑️ Eliminar
                    </button>
                  </td>
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